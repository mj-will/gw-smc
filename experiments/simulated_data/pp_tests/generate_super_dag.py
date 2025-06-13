#!/usr/bin/env
import argparse
import contextlib
import os
import pandas as pd
import shutil


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_ini", type=str)
    parser.add_argument(
        "--outdir",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--injection-file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--prior-file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--detector-frame",
        action="store_true",
    )
    parser.add_argument(
        "--start-time",
        type=float,
        default=1364342418,
    )
    parser.add_argument(
        "--end-time",
        type=float,
        default=1364342930,
    )
    parser.add_argument("--detectors", nargs="+", default=["H1", "V1", "L1"])
    parser.add_argument(
        "--n-injections",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--submit",
        action="store_true",
    )
    parser.add_argument("--superdag-name", type=str, default="gwsmc_superdag")
    return parser


@contextlib.contextmanager
def tmp_working_dir(path):
    """Context manager for using a temporary working directory"""
    d = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(d)


def main(args):
    injections = pd.read_hdf(args.injection_file, key="injections").iloc[
        : args.n_injections
    ]

    os.makedirs(args.outdir, exist_ok=True)

    dags = []

    print(f"Generation configs based on: {args.base_ini}")
    print(f"Output directory: {args.outdir}")

    for i, injection in enumerate(injections.to_dict(orient="records")):
        snrs = {det: injection[f"{det}_snr"] for det in args.detectors}

        data_dict = [
            f"{det}:"
            + os.path.join(
                os.path.abspath(args.data_dir),
                f"injection_{i}_{det}_{int(args.start_time)}_{args.end_time}.hdf5",
            )
            for det in args.detectors
        ]

        arguments = {
            "data-dict": "'{" + ",".join(data_dict) + "}'",
            "outdir": f"injection_{i}",
            "trigger-time": injection["injection_time"],
            "prior-file": "analysis_priors.prior",
        }
        if args.detector_frame:
            detectors_by_snr = sorted(snrs, key=snrs.get, reverse=True)
            arguments["reference-frame"] = "".join(detectors_by_snr)
            arguments["time-reference"] = detectors_by_snr[0]
        else:
            arguments["reference-frame"] = "sky"
            arguments["time-reference"] = "geocent"

        shutil.copyfile(args.base_ini, os.path.join(args.outdir, "base.ini"))
        shutil.copyfile(
            args.prior_file, os.path.join(args.outdir, "analysis_priors.prior")
        )

        with tmp_working_dir(args.outdir):
            # Call bilby_pipe with correct ini file
            args_string = " ".join([f"--{k} {v}" for k, v in arguments.items()])
            for det in args.detectors:
                args_string += f" --detectors {det}"
            os.system(f"bilby_pipe base.ini {args_string} --overwrite-outdir")

        # File the dag file that starts with dag and ends with .submit
        dag_file = [
            f
            for f in os.listdir(os.path.join(args.outdir, f"injection_{i}", "submit"))
            if f.startswith("dag") and f.endswith(".submit")
        ][0]
        dags.append(os.path.join(f"injection_{i}", "submit", dag_file))

    with open(os.path.join(args.outdir, f"{args.superdag_name}.dag"), "w") as f:
        for i, dag in enumerate(dags):
            f.write(f"SUBDAG EXTERNAL Injection{i} {dag}\n")

    if args.submit:
        with tmp_working_dir(args.outdir):
            os.system(f"condor_submit_dag {args.superdag_name}.dag")


if __name__ == "__main__":
    args = get_parser().parse_args()
    main(args)
