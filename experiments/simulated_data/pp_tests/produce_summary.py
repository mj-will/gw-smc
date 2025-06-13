"""Summarize the run statistics for the P-P test runs"""

import argparse
from pathlib import Path
import numpy as np
import re
import h5py


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dirs",
        type=Path,
        default=Path("."),
        nargs="+",
        required=True,
        help="Input directory containing the P-P test results",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Output directory for the renamed files",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default="pp_test_results_summary.hdf5",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--prefix", type=str, default="outdir", help="Prefix for the output directories"
    )
    parser.add_argument(
        "--n-injections", type=int, default=100, help="Number of injections to process"
    )
    return parser


def main(args):
    data = {}
    for path in args.input_dirs:
        if "dynesty" in path.name:
            sampler = "dynesty"
        elif "pocomc" in path.name:
            sampler = "pocomc"
        else:
            raise ValueError(f"Unknown sampler in path: {path}")
        det = re.search(r"(2det|3det)", path.name).group(0)

        if sampler not in data:
            data[sampler] = {}

        n_injections = args.n_injections

        print(f"Producing for {sampler} with {det} in {path}")
        data[sampler][det] = {
            "sampling_time": np.nan * np.zeros(n_injections),
            "likelihood_evaluations": np.nan * np.zeros(n_injections),
            "n_samples": np.nan * np.zeros(n_injections),
            "log_evidence": np.nan * np.zeros(n_injections),
            "log_evidence_error": np.nan * np.zeros(n_injections),
        }
        for i in range(n_injections):
            try:
                result_file = next(
                    (path / f"injection_{i}" / "final_result").glob("*.hdf5")
                )
            except StopIteration:
                raise FileNotFoundError(
                    f"No result file found for injection {i} in {path}"
                )
            with h5py.File(result_file, "r") as f:
                if sampler == "dynesty":
                    data[sampler][det]["sampling_time"][i] = f["sampling_time"][()]
                data[sampler][det]["likelihood_evaluations"][i] = f[
                    "num_likelihood_evaluations"
                ][()]
                data[sampler][det]["n_samples"][i] = len(f["posterior/mass_ratio"][()])
                data[sampler][det]["log_evidence"][i] = f["log_evidence"][()]
                data[sampler][det]["log_evidence_error"][i] = f["log_evidence_err"][()]

            if "pocomc" in sampler:
                # Get the sampling time from the sampling_time.dat file
                # This is a bit of a hack, but it works for now
                try:
                    timing_file = next(
                        (path / f"injection_{i}" / "result").glob(
                            "pocomc*/sampling_time.dat"
                        )
                    )
                except StopIteration:
                    continue
                data[sampler][det]["sampling_time"][i] = np.loadtxt(timing_file)

    with h5py.File(args.output_dir / args.filename, "w") as f:
        for sampler, ndet_dict in data.items():
            sampler_group = f.create_group(sampler)
            for ndet, stats in ndet_dict.items():
                ndet_group = sampler_group.create_group(ndet)
                for key, values in stats.items():
                    ndet_group.create_dataset(key, data=values)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
