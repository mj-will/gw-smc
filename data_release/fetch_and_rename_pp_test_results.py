#!/usr/bin/env python3
import argparse
from pathlib import Path


def get_parser():
    parser = argparse.ArgumentParser(
        description="Fetch and rename result files from P-P test experiment directories."
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
    return parser


def main():

    parser = get_parser()
    args = parser.parse_args()

    injection_dirs = sorted(args.input_dir.glob('injection_*'))

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if not injection_dirs:
        parser.error(f"No injection directories found in '{args.input_dir}'.")

    for inj_dir in injection_dirs:
        final_result_dir = inj_dir / 'final_result'
        if not final_result_dir.is_dir():
            if args.verbose:
                print(f"Skipping {inj_dir}: no final_result directory.")
            continue

        matches = list(final_result_dir.glob("*.hdf5"))
        if not matches:
            if args.verbose:
                print(f"No result file found in {final_result_dir}")
            continue

        src_file = Path(matches[0]).resolve()
        out_filename = f"{args.label}_{inj_dir.name}.hdf5"
        out_path = args.output_dir / out_filename

        # Symbolic link to the source file
        if args.verbose:
            print(f"Linking {src_file} to {out_path}")
        out_path.symlink_to(src_file)

        # If the sampler is pocomc also fetch the sampling_time file
        if "pocomc" in str(src_file):
            result_dir = inj_dir / "result"
            # Find dir that starts with "pocomc"
            pocomc_dirs = sorted(result_dir.glob("pocomc*"))
            if not pocomc_dirs:
                if args.verbose:
                    print(f"No pocomc directory found in {result_dir}")
                continue
            pocomc_dir = pocomc_dirs[0]
            sampling_time_file = (pocomc_dir / "sampling_time.dat").resolve()
            if sampling_time_file.is_file():
                out_sampling_time_path = args.output_dir / f"sampling_time_pocomc_{inj_dir.name}.dat"
                if args.verbose:
                    print(f"Linking {sampling_time_file} to {out_sampling_time_path}")
                out_sampling_time_path.symlink_to(sampling_time_file)
            else:
                if args.verbose:
                    print(f"No sampling time file found in {final_result_dir}")


if __name__ == "__main__":
    main()
