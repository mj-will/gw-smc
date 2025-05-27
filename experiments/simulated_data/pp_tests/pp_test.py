#!/usr/bin/env python
"""
Script to collate result files in nested directories and run a probability-
probability test.

Searches recursively for directories called `final_result` that contain
files with the specified extension.
"""
import argparse
import os
import numpy as np
import tqdm
import pandas as pd
from pathlib import Path
from natsort import natsorted
import json

from bilby.core.result import read_in_result

from gw_smc_utils.plotting import set_style, pp_plot_from_credible_levels


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


def get_parser():
    parser = argparse.ArgumentParser(
        description="Collate result files in nested directories and run a probability-probability test."
    )
    parser.add_argument(
        "--result-dir",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--extension",
        type=str,
        default="hdf5",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--injection-file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--figure-format",
        type=str,
        default="png",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default="pp_test",
    )
    parser.add_argument(
        "--credible-levels-file",
        type=str,
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite the credible levels file if it exists.",
    )
    return parser


def discover_result_files(result_dir, extension):
    result_files = {}
    for dirpath, _, filenames in os.walk(result_dir):
        if "final_result" in dirpath:
            for filename in filenames:
                if filename.endswith(extension):
                    # Get the injection ID from the path with formation `injection_<id>/final_result/some-file-name.hdf5`
                    inj_id = os.path.basename(os.path.dirname(dirpath)).split("_")[-1]
                    result_files[inj_id] = os.path.join(dirpath, filename)

    # Sort the result files by injection ID
    result_files = dict(natsorted(result_files.items()))
    return result_files


def main(args):

    set_style()

    injection_parameters = pd.read_hdf(args.injection_file, key="injections")
    injection_parameters["mass_ratio"].hist()
    injection_parameters = injection_parameters.to_dict(orient="records")

    if args.outdir is None:
        outdir = args.result_dir
    else:
        outdir = args.outdir
        outdir.mkdir(exist_ok=True, parents=True)

    keys = [
        "chirp_mass",
        "mass_ratio",
        "a_1",
        "a_2",
        "tilt_1",
        "tilt_2",
        "phi_12",
        "phi_jl",
        "luminosity_distance",
        "dec",
        "ra",
        "theta_jn",
        "psi",
        "geocent_time",
        "phase",
    ]

    credible_levels_filename = args.credible_levels_file

    if credible_levels_filename is not None:
        credible_levels_filename = Path(credible_levels_filename)
        credible_levels_filename.parent.mkdir(exist_ok=True, parents=True)

    if credible_levels_filename.exists() and not args.overwrite:
        print(f"Loading credible levels from {credible_levels_filename}")
        # Load credible levels from a file if provided
        credible_levels = pd.read_hdf(credible_levels_filename, key="credible_levels")
        if not set(keys).issubset(set(credible_levels.columns)):
            raise ValueError("Credible levels file does not contain all keys.")
    else:
        result_files = discover_result_files(args.result_dir, args.extension)

        print(f"Found {len(result_files)} result files")
        print("Reading in results")
        results = []
        for rf in tqdm.tqdm(result_files.values()):
            results.append(read_in_result(rf))
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
        credible_levels.to_hdf(
            credible_levels_filename,
            key="credible_levels",
            mode="w",
            format="table",
            data_columns=True,
        )

    print("Producing P-P plot")
    fig, p_values = pp_plot_from_credible_levels(
        credible_levels=credible_levels,
    )
    filename = outdir / f"{args.filename}.{args.figure_format}"
    fig.savefig(filename)

    with open(outdir / "p_values.json", "w") as f:
        json.dump(p_values._asdict(), f)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
