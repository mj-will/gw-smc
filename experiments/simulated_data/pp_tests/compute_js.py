"""Compute the JSD

Note this code is not optimized and may take several hours to run.
"""
import argparse
import os
import natsort
import glob
import json
import tqdm
import numpy as np
from gw_smc_utils import js
from gw_smc_utils.posterior import load_bilby_posterior
from gw_smc_utils.utils import get_bilby_prior


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dirs", nargs="+")
    parser.add_argument("--filename", type=str)
    parser.add_argument("--base", type=float, default=2)
    parser.add_argument("--verbose", action="store_true")
    return parser


PARAMETERS = [
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
]


def main(result_dirs, filename, extension="hdf5", base=2, seed=1234, verbose=False):

    os.makedirs("results", exist_ok=True)

    rng = np.random.default_rng(seed)

    result_files = []
    for d in result_dirs:
        result_files.append(
            natsort.natsorted(glob.glob(os.path.join(d, f"*.{extension}")))[:2]
        )
    jsd = {
        "res1": result_dirs[0],
        "res2": result_dirs[1],
        "base": base,
    }

    priors = get_bilby_prior(result_files[0][0])
    priors_alt = get_bilby_prior(result_files[1][0])
    if priors != priors_alt:
        raise ValueError("Priors are not the same")

    for (i, res1_file), res2_file in tqdm.tqdm(zip(enumerate(result_files[0]), result_files[1])):
        jsd[i] = {}
        post1 = load_bilby_posterior(res1_file, PARAMETERS)
        post2 = load_bilby_posterior(res2_file, PARAMETERS)

        for key in PARAMETERS:
            if verbose:
                print(f"Calculating JSD for {key}")
            jsd[i][key] = js.calculate_js(
                post1[key],
                post2[key],
                base=base,
                rng=rng,
                lower_bound=priors[key].minimum,
                upper_bound=priors[key].maximum,
                boundary_type=priors[key].boundary,
                verbose=verbose,
                kde_class="NaiveKDE",
            )

    with open(filename, "w") as fp:
        json.dump(jsd, fp)


if __name__ == "__main__":
    args = create_parser().parse_args()
    main(
        args.result_dirs,
        filename=args.filename,
        base=args.base,
        verbose=args.verbose,
    )
