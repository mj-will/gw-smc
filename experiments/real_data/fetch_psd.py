#!/usr/bin/env
"""
Script to fetch the PSD from GWTC-2.1/3 data releases and save them in
<SID>/psds/<key>-psd.dat.
"""

import argparse
import pathlib
import h5py
import numpy as np

from gw_smc_utils.results import find_gwtc_results


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--SID", type=str)
    parser.add_argument(
        "--data-releases", nargs="+", type=str, default=["GWTC-2.1", "GWTC-3"]
    )
    parser.add_argument("--data-release-path", type=str, default="data_releases")
    parser.add_argument("--cosmo", action="store_true")
    parser.add_argument("--analysis", type=str, default="C01:IMRPhenomXPHM")
    return parser


def main(args):
    filepath, release = find_gwtc_results(
        args.data_release_path, args.data_releases, args.SID, args.cosmo
    )

    outdir = pathlib.Path(args.SID) / "psds"
    outdir.mkdir(parents=True, exist_ok=True)

    with h5py.File(filepath, "r") as f:
        for key, psd in f[f"{args.analysis}/psds"].items():
            np.savetxt(outdir / f"{key}-psd.dat", psd)


if __name__ == "__main__":
    args = get_parser().parse_args()
    main(args)
