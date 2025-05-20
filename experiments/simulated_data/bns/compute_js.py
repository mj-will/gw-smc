#!/usr/bin/env python
"""Compute the JSD

Note this code is not optimized and may take several hours to run.
"""
import argparse
import os
import json
import numpy as np
from pathlib import Path
import re
from gw_smc_utils import js
from gw_smc_utils.posterior import load_bilby_posterior
from gw_smc_utils.utils import get_bilby_prior


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default=Path("."))
    parser.add_argument("--results", type=Path, nargs=2, default=[])
    parser.add_argument("--label", type=str, default="")
    parser.add_argument("--prefix", default=None, type=str)
    parser.add_argument("--run-labels", type=str, nargs=2, default=["", ""])
    parser.add_argument("--samplers", type=str, nargs=2)
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--base", type=float, default=2)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--n-samples", type=int, default=5000)
    parser.add_argument("--n-tests", type=int, default=10)
    parser.add_argument("--n-pool", type=int, default=None)
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
    "lambda_1",
    "lambda_2",
    "chi_1",
    "chi_2",
]

def find_result_file_pairs(directory, samplers, prefix, run_labels):
    paths = {}
    for sampler, label in zip(samplers, run_labels):
        print(sampler, label)
        paths[sampler] = list(Path(directory).glob(f"{prefix}*{sampler}*{label}/**/final_result/{sampler}*.hdf5"))
    print(paths)
    labels = {}
    for i, sampler in enumerate(samplers):
        labels[sampler] = {"2det": [], "3det": []}
        raw_labels = [path.parents[1].name.split(sampler)[-1] for path in paths[sampler]]
        # Search for number of detectors (e.g. 2det or 3det)
        for rl in raw_labels:
            n_det = re.search(r"\d+det", rl).group(0)
            if n_det in labels[sampler]:
                label = rl.split(n_det)[-1]
                if run_labels[i] in label:
                    label = label.replace(run_labels[i], "")
                if label[0] == "_":
                    label = label[1:]
                if label[-1] == "_":
                    label = label[:-1]
                labels[sampler][n_det].append(label)
            else:
                raise ValueError(f"Unknown number of detectors: {n_det}")
    
    result_file_pairs = []
    for n_det in ["2det", "3det"]:
        all_labels = set(labels[samplers[0]][n_det]).intersection(set(labels[samplers[1]][n_det]))
        for label in all_labels:
            det_label = f"{n_det}_{label}"
            pattern = re.compile(rf".*{n_det}_{label}.*")
            pair = {det_label: (
                *[p for p in paths[samplers[0]] if pattern.match(p.name)],
                *[p for p in paths[samplers[1]] if pattern.match(p.name)],
            )}
            if len(pair[det_label]) != 2:
                print(f"Could not find a pair for {n_det}_{label}")
                continue
            result_file_pairs.append(pair)
        extra = set(labels[samplers[0]][n_det]).symmetric_difference(set(labels[samplers[1]][n_det]))
        if extra:
            print(f"Missing some results for {n_det}: {extra}")
    return result_file_pairs


def compute_js(result_files, filename, base, seed, verbose, n_samples, n_tests, n_pool, rng):
    jsd = {
        "res1": str(result_files[0]),
        "res2": str(result_files[1]),
        "base": base,
        "seed": seed,
        "n_samples": n_samples,
        "n_tests": n_tests,
        "jsd": {},
    }

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
                if key not in post1:
                    print(f"Key {key} not found in post1, skipping")
                else:
                    print(f"Calculating JSD for {key}")
            
            if key not in post1 or key not in post2:
                continue

            try:
                boundary = priors[key].boundary
            except KeyError:
                continue
            # These parameters are bounded but have zero prior probability at
            # the boundary, so we can treat them as unbounded
            if key in ["theta_jn", "tilt_1", "tilt_2", "dec"]:
                boundary = "none"

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
            )

    dir = os.path.split(filename)[0]
    os.makedirs(dir, exist_ok=True)

    with open(filename, "w") as fp:
        json.dump(jsd, fp, indent=4)


def parse_label(label):
    if label.lower() == "none":
        return ""
    return label


def main(
    directory: Path,
    samplers: list[str],
    prefix: str,
    run_labels: list[str],
    outdir: Path,
    base: float = 2,
    seed: int = 1234,
    verbose: bool = False,
    n_samples: int = 1000,
    n_tests: int = 10,
    n_pool: int | None = None,
):

    run_labels = [parse_label(label) for label in run_labels]

    if args.results:
        result_file_pairs = [{args.label: args.results}]
        print(result_file_pairs)
    else:
        result_file_pairs = find_result_file_pairs(directory, samplers, prefix, run_labels)
        print(f"Found {len(result_file_pairs)} result file pairs")
    if not result_file_pairs:
        print("No result file pairs found")
        exit()

    outdir.mkdir(parents=True, exist_ok=True)

    for pair in result_file_pairs:
        label, result_files = pair.popitem()
        rng = np.random.default_rng(seed)
        filename = outdir / f"{label}_jsd.json"
        compute_js(
            result_files=result_files,
            filename=filename,
            base=base,
            seed=seed,
            verbose=verbose,
            n_samples=n_samples,
            n_tests=n_tests,
            n_pool=n_pool,
            rng=rng,
        )


if __name__ == "__main__":
    args = create_parser().parse_args()
    main(
        directory=args.directory,
        samplers=args.samplers,
        prefix=args.prefix,
        run_labels=args.run_labels,
        outdir=args.outdir,
        base=args.base,
        verbose=args.verbose,
        n_samples=args.n_samples,
        n_tests=args.n_tests,
        n_pool=args.n_pool,
    )
