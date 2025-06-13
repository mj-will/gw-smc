from collections import namedtuple
import importlib
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
from pesummary.gw.plots.latex_labels import GWlatex_labels
import re
import shutil


def set_style() -> None:
    """Set the plotting style"""
    with importlib.resources.path("gw_smc_utils", "paper.mplstyle") as p:
        plt.style.use(p)
    # Disable LaTeX rendering if latex is not installed
    from matplotlib import rcParams

    rcParams["text.usetex"] = True if shutil.which("latex") else False


def lighten_colour(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Copied from: https://gist.github.com/ihincks/6a420b599f43fcd7dbd79d56798c4e5a

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys

    try:
        c = mc.cnames[color]
    except KeyError:
        c = color
    c = np.array(colorsys.rgb_to_hls(*mc.to_rgb(c)))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


def pp_plot_from_credible_levels(
    credible_levels,
    confidence_interval=[0.68, 0.95, 0.997],
    lines=None,
    legend_fontsize="x-small",
    title=True,
    confidence_interval_alpha=0.1,
    **kwargs,
):
    """
    Make a P-P plot from a dataframe of credible levels.
    """
    if lines is None:
        colors = ["C{}".format(i) for i in range(8)]
        linestyles = ["-", "--", ":"]
        lines = ["{}{}".format(a, b) for a, b in product(linestyles, colors)]
    if len(lines) < len(credible_levels.keys()):
        raise ValueError("Larger number of parameters than unique linestyles")

    x_values = np.linspace(0, 1, 1001)

    N = len(credible_levels)

    figsize = plt.rcParams["figure.figsize"].copy()
    # figsize[1] = 1.5 * figsize[1]
    fig, ax = plt.subplots(figsize=figsize)

    if isinstance(confidence_interval, float):
        confidence_interval = [confidence_interval]
    if isinstance(confidence_interval_alpha, float):
        confidence_interval_alpha = [confidence_interval_alpha] * len(
            confidence_interval
        )
    elif len(confidence_interval_alpha) != len(confidence_interval):
        raise ValueError(
            "confidence_interval_alpha must have the same length as confidence_interval"
        )

    for ci, alpha in zip(confidence_interval, confidence_interval_alpha):
        edge_of_bound = (1.0 - ci) / 2.0
        lower = scipy.stats.binom.ppf(1 - edge_of_bound, N, x_values) / N
        upper = scipy.stats.binom.ppf(edge_of_bound, N, x_values) / N
        # The binomial point percent function doesn't always return 0 @ 0,
        # so set those bounds explicitly to be sure
        lower[0] = 0
        upper[0] = 0
        ax.fill_between(x_values, lower, upper, alpha=alpha, color="k")

    pvalues = []
    print("Key: KS-test p-value")
    for ii, key in enumerate(credible_levels):
        pp = np.array(
            [
                sum(credible_levels[key].values < xx) / len(credible_levels)
                for xx in x_values
            ]
        )
        pvalue = scipy.stats.kstest(credible_levels[key], "uniform").pvalue
        pvalues.append(pvalue)
        print(f"{key}: {pvalue}")

        name = GWlatex_labels.get(key, key)
        name = re.sub(r"\[.*?\]", "", name)
        label = "{} ({:2.3f})".format(name, pvalue)
        plt.plot(x_values, pp, lines[ii], label=label, **kwargs)

    Pvals = namedtuple("pvals", ["combined_pvalue", "pvalues", "names"])
    pvals = Pvals(
        combined_pvalue=scipy.stats.combine_pvalues(pvalues)[1],
        pvalues=pvalues,
        names=list(credible_levels.keys()),
    )
    print("Combined p-value: {}".format(pvals.combined_pvalue))

    if title:
        ax.set_title(
            "N={}, $p$-value={:2.4f}".format(
                len(credible_levels), pvals.combined_pvalue
            )
        )
    ax.set_xlabel("C.I.")
    ax.set_ylabel("Fraction of events in C.I.")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.legend(
        handlelength=2,
        labelspacing=0.25,
        fontsize=legend_fontsize,
        loc="center",
        bbox_to_anchor=(0.55, -0.15),
        ncol=2,
    )
    fig.tight_layout()
    return fig, pvals
