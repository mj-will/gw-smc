"""Code to generate ini files that use the detector frame.

These require standard tests to have been run first.
"""
import argparse
import glob
import string
import tqdm
import numpy as np
import natsort
import os
from bilby_pipe.utils import DataDump
import yaml
import re
import contextlib
import subprocess


@contextlib.contextmanager
def tmp_working_dir(path):
    """Context manager for using a temporary working directory"""
    d = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(d)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-ini", type=str, required=True)
    parser.add_argument("--config-file", type=str, required=True)
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--n-injections", type=int, default=None)
    parser.add_argument("--indices", type=int, nargs="+", default=None)
    parser.add_argument("--sleep-time", type=float, default=0.0)
    return parser


def main():
    args = get_parser().parse_args()

    with open(args.template_ini, "r") as f:
        template = string.Template(f.read())

    with open(args.config_file, "r") as f:
        config = yaml.safe_load(f)

    data_dump_files = natsort.natsorted(glob.glob(f"{config['data_dump_dir']}/*.pickle"))

    if args.indices is not None and args.n_injections is not None:
        raise ValueError("Cannot specify both indices and n_injections")

    if args.indices is not None:
        data_dump_files = [data_dump_files[i] for i in args.indices]
    elif args.n_injections is not None:
        data_dump_files = data_dump_files[:args.n_injections]

    for ddf in tqdm.tqdm(data_dump_files):
        match = re.search(r'data(\d+)_', ddf)
        if match:
            i = int(match.group(1))
        else:
            raise ValueError(f"Could not extract number from {ddf}")

        data_dump = DataDump.from_pickle(ddf)

        snrs = {}
        for ifo in data_dump.interferometers:
            if ifo.name in config["detectors"]:
                snrs[ifo.name] = np.abs(ifo.meta_data["matched_filter_SNR"])

        if "time_reference" in config:
            time_reference = config["time_reference"]
        else:
            # Time reference should be IFO with max SNR
            time_reference = max(snrs, key=snrs.get)

        if "reference_frame" in config:
            reference_frame = config["reference_frame"]
        else:
            # Sort IFOs by SNR and join for reference frame
            reference_frame = "".join(sorted(snrs, key=snrs.get, reverse=True))

        label = f"{config['label']}_inj{i}"
        inj_outdir = label
        os.makedirs(inj_outdir, exist_ok=True)
        ini_file = template.safe_substitute(
            {
                "label": label,
                "detectors": ",".join(config["detectors"]),
                "outdir": inj_outdir,
                "reference_frame": reference_frame,
                "time_reference": time_reference,
                "sampler": config["sampler"],
                "sampler_kwargs": config["sampler_kwargs"],
                "injection_id": i,
                "phase_parameter": config["phase_parameter"].replace("-", "_"),
                "injection_file": config["injection_file"],
                "generation_seed": config["seed"] + i,
            }
        )

        outdir = config["outdir"]
        os.makedirs(outdir, exist_ok=True)
        ini_file_name = f"{config['label']}_inj{i}.ini"
        ini_path = os.path.join(outdir, ini_file_name)
        with open(ini_path, "w") as f:
            f.write(ini_file)

        injection_file_abs = os.path.abspath(config["injection_file"])
        sym_inj_file = os.path.join(outdir, config["injection_file"])
        if not os.path.exists(sym_inj_file):
            os.symlink(injection_file_abs, sym_inj_file)

        if args.submit:
            print(f"Submitting run for injection {i}")
            with tmp_working_dir(outdir):
                subprocess.run(["bilby_pipe", ini_file_name, "--submit"])
        else:
            with tmp_working_dir(outdir):
                subprocess.run(["bilby_pipe", ini_file_name])

        if args.sleep_time > 0:
            import time
            time.sleep(args.sleep_time)


if __name__ == "__main__":
    main()
