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
    parser.add_argument("--data-dump-dir", type=str, required=True)
    parser.add_argument("--submit", action="store_true")
    return parser


def main():
    args = get_parser().parse_args()

    with open(args.template_ini, "r") as f:
        template = string.Template(f.read())

    with open(args.config_file, "r") as f:
        config = yaml.safe_load(f)

    data_dump_files = natsort.natsorted(glob.glob(f"{args.data_dump_dir}/*.pickle"))

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

        # Time reference should be IFO with max SNR
        time_reference = max(snrs, key=snrs.get)
        # Sort IFOs by SNR and join for reference frame
        reference_frame = "".join(sorted(snrs, key=snrs.get, reverse=True))

        outdir = os.path.join(config["outdir"], f"{config['label']}_inj_{i}")
        os.makedirs(outdir, exist_ok=True)
        ini_file = template.safe_substitute(
            {
                "label": "det_frame_test",
                "detectors": ",".join(config["detectors"]),
                "outdir": f"outdir_inj_{i}",
                "reference_frame": reference_frame,
                "time_reference": time_reference,
                "sampler": config["sampler"],
                "sampler_kwargs": config["sampler_kwargs"],
                "injection_id": i,
                "phase_parameter": config["phase_parameter"].replace("-", "_"),
                "injection_file": config["injection_file"]
            }
        )

        ini_file_name = f"{config['label']}.ini"
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
        

if __name__ == "__main__":
    main()
