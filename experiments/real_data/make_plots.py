import argparse
from pesummary.io import read as pesummary_read
from pesummary.utils.samples_dict import MultiAnalysisSamplesDict
import matplotlib.pyplot as plt
from pathlib import Path

from gw_smc_utils.results import find_gwtc_results


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", nargs="+", type=Path)
    parser.add_argument("--labels", nargs="+", type=str)
    parser.add_argument("--output", type=Path, default=Path("figures"))
    parser.add_argument("--SID", type=str, required=True)
    parser.add_argument("--data-releases", nargs="+", type=str, default=["GWTC-2.1", "GWTC-3"])
    parser.add_argument("--data-release-path", type=str, default="data_releases")
    parser.add_argument("--cosmo", action="store_true")
    return parser


def main(args):
    print(args)
    filepath, release = find_gwtc_results(
        args.data_release_path, args.data_releases, args.SID, args.cosmo
    )
    analysis_key = "C01:IMRPhenomXPHM"
    lvk_result = pesummary_read(filepath)

    output = args.output
    output.mkdir(exist_ok=True, parents=True)

    labels = args.labels if args.labels else [f"result_{i}" for i in range(len(args.results))]

    results = {}

    for label, result_file in zip(labels, args.results):
        results[label] = pesummary_read(str(result_file))

    samples = MultiAnalysisSamplesDict({
        release: lvk_result.samples_dict[analysis_key],
        **{k: v.samples_dict for k, v in results.items()}
    })

    plot_parameters = {
        "instrinsic": ["mass_1_source", "mass_2_source", "chi_eff", "chi_p"],
        "localization": ["ra", "dec", "luminosity_distance", "theta_jn"],
    }

    for key, parameters in plot_parameters.items():
        samples.plot(
            parameters=parameters,
            labels=[release] + labels,
            type="corner"
        )
        plt.savefig(output / f"{args.SID}_{key}.pdf")


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
