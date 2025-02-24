#!/usr/bin/env python
"""
Script to collate result files in nested directories and run a probability-
probability test.

Searches recursively for directories called `final_result` that contain
files with the specified extension.
"""
import argparse
from itertools import product
from collections import namedtuple
import os
import numpy as np
import tqdm
import pandas as pd
import scipy.stats
import matplotlib.pyplot as plt
from natsort import natsorted

from bilby.core.result import read_in_result


def get_injection_credible_level(result, parameter, injection_parameters, weights=None):
    if weights is None:
        weights = np.ones(len(result.posterior[parameter]))
    if parameter not in injection_parameters:
        raise ValueError(f"Parameter {parameter} not found in injections")
    credible_level = (
        np.sum(np.array(result.posterior[parameter] < injection_parameters[parameter]) * weights) / np.sum(weights)
    )
    return credible_level


def get_all_credible_levels(result, injection_parameters, keys, weights=None):
    return {
        key: get_injection_credible_level(result, key, injection_parameters, weights=weights)
        for key in keys
    }


def make_pp_plot(
    results,
    injection_parameters,
    confidence_interval=[0.68, 0.95, 0.997],
    lines=None,
    legend_fontsize='x-small',
    keys=None,
    title=True,
    confidence_interval_alpha=0.1,
    weight_list=None,
    **kwargs
):
    """
    Make a P-P plot for a set of runs with injected signals.

    Parameters
    ==========
    results: list
        A list of Result objects, each of these should have injected_parameters
    filename: str, optional
        The name of the file to save, the default is "outdir/pp.png"
    save: bool, optional
        Whether to save the file, default=True
    confidence_interval: (float, list), optional
        The confidence interval to be plotted, defaulting to 1-2-3 sigma
    lines: list
        If given, a list of matplotlib line formats to use, must be greater
        than the number of parameters.
    legend_fontsize: float
        The font size for the legend
    keys: list
        A list of keys to use, if None defaults to search_parameter_keys
    title: bool
        Whether to add the number of results and total p-value as a plot title
    confidence_interval_alpha: float, list, optional
        The transparency for the background condifence interval
    weight_list: list, optional
        List of the weight arrays for each set of posterior samples.
    kwargs:
        Additional kwargs to pass to matplotlib.pyplot.plot

    Returns
    =======
    fig, pvals:
        matplotlib figure and a NamedTuple with attributes `combined_pvalue`,
        `pvalues`, and `names`.
    """
    import matplotlib.pyplot as plt

    if keys is None:
        keys = results[0].search_parameter_keys

    if weight_list is None:
        weight_list = [None] * len(results)

    credible_levels = list()
    for i, result in enumerate(results):
        credible_levels.append(
            get_all_credible_levels(
                result=result,
                injection_parameters=injection_parameters[i],
                keys=keys,
            )
        )
    credible_levels = pd.DataFrame(credible_levels)

    if lines is None:
        colors = ["C{}".format(i) for i in range(8)]
        linestyles = ["-", "--", ":"]
        lines = ["{}{}".format(a, b) for a, b in product(linestyles, colors)]
    if len(lines) < len(credible_levels.keys()):
        raise ValueError("Larger number of parameters than unique linestyles")

    x_values = np.linspace(0, 1, 1001)

    N = len(credible_levels)
    fig, ax = plt.subplots()

    if isinstance(confidence_interval, float):
        confidence_interval = [confidence_interval]
    if isinstance(confidence_interval_alpha, float):
        confidence_interval_alpha = [confidence_interval_alpha] * len(confidence_interval)
    elif len(confidence_interval_alpha) != len(confidence_interval):
        raise ValueError(
            "confidence_interval_alpha must have the same length as confidence_interval")

    for ci, alpha in zip(confidence_interval, confidence_interval_alpha):
        edge_of_bound = (1. - ci) / 2.
        lower = scipy.stats.binom.ppf(1 - edge_of_bound, N, x_values) / N
        upper = scipy.stats.binom.ppf(edge_of_bound, N, x_values) / N
        # The binomial point percent function doesn't always return 0 @ 0,
        # so set those bounds explicitly to be sure
        lower[0] = 0
        upper[0] = 0
        ax.fill_between(x_values, lower, upper, alpha=alpha, color='k')

    pvalues = []
    print("Key: KS-test p-value")
    for ii, key in enumerate(credible_levels):
        pp = np.array([sum(credible_levels[key].values < xx) /
                       len(credible_levels) for xx in x_values])
        pvalue = scipy.stats.kstest(credible_levels[key], 'uniform').pvalue
        pvalues.append(pvalue)
        print(f"{key}: {pvalue}")

        try:
            name = results[0].priors[key].latex_label
        except (AttributeError, KeyError):
            name = key
        label = "{} ({:2.3f})".format(name, pvalue)
        plt.plot(x_values, pp, lines[ii], label=label, **kwargs)

    Pvals = namedtuple('pvals', ['combined_pvalue', 'pvalues', 'names'])
    pvals = Pvals(combined_pvalue=scipy.stats.combine_pvalues(pvalues)[1],
                  pvalues=pvalues,
                  names=list(credible_levels.keys()))
    print(
        "Combined p-value: {}".format(pvals.combined_pvalue))

    if title:
        ax.set_title("N={}, p-value={:2.4f}".format(
            len(results), pvals.combined_pvalue))
    ax.set_xlabel("C.I.")
    ax.set_ylabel("Fraction of events in C.I.")
    ax.legend(handlelength=2, labelspacing=0.25, fontsize=legend_fontsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    return fig, pvals


def get_parser():
    parser = argparse.ArgumentParser(
        description="Collate result files in nested directories and run a probability-probability test."
    )
    parser.add_argument(
        "--result-dir",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--extension",
        type=str,
        default="hdf5",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--injection-file",
        type=str,
        required=True,
    )
    return parser


def main(args):

    injection_parameters = pd.read_hdf(args.injection_file, key="injections")
    injection_parameters["mass_ratio"].hist()
    plt.savefig("chirp_mass.png")
    injection_parameters = injection_parameters.to_dict(orient="records")

    # Recursively find all result files
    result_files = {}
    for dirpath, _, filenames in os.walk(args.result_dir):
        if "final_result" in dirpath:
            for filename in filenames:
                if filename.endswith(args.extension):
                    # Get the injection ID from the path with formation `injection_<id>/final_result/some-file-name.hdf5`
                    inj_id = os.path.basename(os.path.dirname(dirpath)).split("_")[-1]
                    result_files[inj_id] = os.path.join(dirpath, filename)

    # Sort the result files by injection ID
    result_files = dict(natsorted(result_files.items()))
    print(result_files)

    print(f"Found {len(result_files)} result files")
    print("Reading in results")
    results = []
    for rf in tqdm.tqdm(result_files.values()):
        results.append(read_in_result(rf))

    if args.outdir is None:
        outdir = args.result_dir
    else:
        outdir = args.outdir
        os.makedirs(outdir, exist_ok=True)

    print("Producing P-P plot")
    fig, p_values = make_pp_plot(
        results,
        injection_parameters=injection_parameters,
    )
    filename = os.path.join(outdir, "pp_test.png")

    fig.savefig(filename)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
