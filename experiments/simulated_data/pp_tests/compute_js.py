#!/usr/bin/env python
"""Compute the JSD

Note this code is not optimized and may take several hours to run.
"""

import argparse
import os
import json
import numpy as np
from gw_smc_utils import js
from gw_smc_utils.posterior import load_bilby_posterior
from gw_smc_utils.utils import get_bilby_prior


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("result_files", nargs=2)
    parser.add_argument("--filename", type=str)
    parser.add_argument("--base", type=float, default=2)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--n-samples", type=int, default=5000)
    parser.add_argument("--xsteps", type=int, default=100)
    parser.add_argument("--n-tests", type=int, default=10)
    parser.add_argument("--n-pool", type=int, default=None)
    parser.add_argument("--use-pesummary", action="store_true")
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
    "phase",
    "zenith",
    "azimuth",
    "H1_time",
    "L1_time",
    "V1_time",
]


def main(
    result_files: list[str],
    filename: str,
    base: float = 2,
    seed: int = 1234,
    verbose: bool = False,
    n_samples: int = 1000,
    n_tests: int = 10,
    n_pool: int | None = None,
    use_pesummary: bool = False,
    xsteps: int = 100,
):
    os.makedirs("results", exist_ok=True)

    rng = np.random.default_rng(seed)

    jsd = {
        "res1": result_files[0],
        "res2": result_files[1],
        "base": base,
        "seed": seed,
        "n_samples": n_samples,
        "n_tests": n_tests,
        "xsteps": xsteps,
        "use_pesummary": use_pesummary,
        "jsd": {},
    }

    if verbose:
        print(f"Settings: {jsd}")

    if use_pesummary:
        print("Using pesummary for JSD calculation. This will ignore other settings")
        jsd["n_samples"] = None
        jsd["n_tests"] = None
        jsd["seed"] = None

    priors = get_bilby_prior(result_files[0])
    priors_alt = get_bilby_prior(result_files[1])
    if priors != priors_alt:
        raise ValueError("Priors are not the same")

    post1 = load_bilby_posterior(result_files[0], PARAMETERS)
    post2 = load_bilby_posterior(result_files[1], PARAMETERS)

    if n_pool is not None:
        from multiprocessing import Pool

    else:
        from multiprocessing.dummy import Pool

        n_pool = 1

    with Pool(n_pool) as pool:
        for key in PARAMETERS:
            if verbose:
                print(f"Calculating JSD for {key}")

            if key not in post1:
                print(f"Warning: {key} not in posterior A")
                continue
            if key not in post2:
                print(f"Warning: {key} not in posterior B")
                continue

            if key not in priors:
                print(f"Warning: {key} not in priors")
                continue
            boundary = priors[key].boundary
            # These parameters are bounded but have zero prior probability at
            # the boundary, so we can treat them as unbounded
            if key in ["theta_jn", "tilt_1", "tilt_2", "dec"]:
                boundary = "none"

            if not use_pesummary:
                jsd["jsd"][key] = js.calculate_js(
                    post1[key],
                    post2[key],
                    base=base,
                    rng=rng,
                    lower_bound=priors[key].minimum,
                    upper_bound=priors[key].maximum,
                    boundary_type=boundary,
                    verbose=verbose,
                    n_samples=n_samples,
                    n_tests=n_tests,
                    pool=pool,
                    xsteps=xsteps,
                )
            else:
                from pesummary.utils.utils import jensen_shannon_divergence_from_samples

                samples = [post1[key], post2[key]]
                jsd["jsd"][key] = jensen_shannon_divergence_from_samples(
                    samples=samples,
                    base=base,
                )

    dir = os.path.split(filename)[0]
    os.makedirs(dir, exist_ok=True)

    with open(filename, "w") as fp:
        json.dump(jsd, fp, indent=4)


if __name__ == "__main__":
    args = create_parser().parse_args()
    main(
        args.result_files,
        filename=args.filename,
        base=args.base,
        verbose=args.verbose,
        n_samples=args.n_samples,
        n_tests=args.n_tests,
        n_pool=args.n_pool,
        use_pesummary=args.use_pesummary,
        xsteps=args.xsteps,
    )
