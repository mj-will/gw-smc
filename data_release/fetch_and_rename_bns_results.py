#!/usr/bin/env python3
import argparse
from pathlib import Path
import re


def get_parser():
    parser = argparse.ArgumentParser(
        description="Fetch and rename result files from BNS runs."
    )
    parser.add_argument(
        '--input-dir', type=Path,
        help="Input directory containing the P-P test results",
    )
    parser.add_argument(
        '--label', type=str,
        help="Label used for the new files"
    )
    parser.add_argument(
        '--output-dir', type=Path,
        help="Output directory for the renamed files",
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help="Enable verbose output"
    )
    parser.add_argument(
        '--prefix',
        type=str,
        default="outdir",
        help="Prefix for the output directories"
    )
    return parser


def main():

    parser = get_parser()
    args = parser.parse_args()

    outdirs = sorted(args.input_dir.glob(f'{args.prefix}_*'))

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if not outdirs:
        parser.error(f"No output directories found in '{args.input_dir}'.")

    for run_outdir in outdirs:
        if "dynesty" in run_outdir.name:
            sampler = "dynesty"
        elif "pocomc" in run_outdir.name:
            sampler = "pocomc"
        else:
            raise ValueError(f"Unknown sampler in directory name: {run_outdir}")
        
        # Match pattern 2det or 3det
        match = re.search(r'(2det|3det)', run_outdir.name)
        ndet = match.group(1) if match else None
        if ndet is None:
            raise ValueError(f"Could not determine number of detectors from directory name: {run_outdir}")

        config_name = run_outdir.name.split(ndet)[-1].strip('_')

        final_result_dir = run_outdir / 'final_result'
        if not final_result_dir.is_dir():
            if args.verbose:
                print(f"Skipping {run_outdir}: no final_result directory.")
            continue

        matches = list(final_result_dir.glob("*.hdf5"))
        if not matches:
            if args.verbose:
                print(f"No final result files found in {final_result_dir}")
            continue
        if len(matches) > 1:
            raise ValueError(f"Multiple final result files found in {final_result_dir}: {matches}")
        final_result_file = matches[0]
        src_file = final_result_file.resolve()
        out_filename = f"{args.label}_{sampler}_{ndet}_{config_name}_merge_result.hdf5"
        out_path = args.output_dir / out_filename
        # Symbolic link to the source file
        if args.verbose:
            print(f"Linking {src_file} to {out_path}")
        out_path.symlink_to(src_file)


        result_dir = run_outdir / 'result'
        if not result_dir.is_dir():
            if args.verbose:
                print(f"Skipping {run_outdir}: no final_result directory.")
            continue

        matches = list(result_dir.glob("*par*.hdf5"))
        if not matches:
            if args.verbose:
                print(f"No result files found in {result_dir}")
            continue

        for match in matches:
            par_match = re.search(r'par(\d+)', match.name)
            par = par_match.group(1)
            src_file = Path(match).resolve()
            out_filename = f"{args.label}_{sampler}_{ndet}_{config_name}_par{par}.hdf5"
            out_path = args.output_dir / out_filename

            # Symbolic link to the source file
            if args.verbose:
                print(f"Linking {src_file} to {out_path}")
            out_path.symlink_to(src_file)

if __name__ == "__main__":
    main()
