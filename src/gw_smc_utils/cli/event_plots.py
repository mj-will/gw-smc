import argparse
from pesummary.io import read as pesummary_read
from pesummary.utils.samples_dict import MultiAnalysisSamplesDict
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from gw_smc_utils.results import find_gwtc_results
from gw_smc_utils.plotting import set_style

set_style()


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", nargs="+", type=Path)
    parser.add_argument("--labels", nargs="+", type=str)
    parser.add_argument("--output", type=Path, default=Path("figures"))
    parser.add_argument("--SID", type=str, required=True)
    parser.add_argument("--data-releases", nargs="+", type=str, default=["GWTC-2.1", "GWTC-3"])
    parser.add_argument("--data-release-path", type=str, default="data_releases")
    parser.add_argument("--cosmo", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--extension", type=str, default="pdf",
                        choices=["pdf", "png", "svg", "jpg"],
                        help="File extension for the output figures.")
    return parser


def main():

    parser = get_parser()
    args = parser.parse_args()

    np.random.seed(args.seed)

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

    n_samples = 10_000

    samples = MultiAnalysisSamplesDict({
        release: lvk_result.samples_dict[analysis_key].downsample(n_samples),
        **{k: v.samples_dict.downsample(n_samples) for k, v in results.items()}
    })

    plot_parameters = {
        "intrinsic": ["mass_1_source", "mass_2_source", "chi_eff", "chi_p"],
        "localization": ["ra", "dec", "luminosity_distance", "theta_jn"],
    }

    with plt.rc_context({
        "legend.fontsize": 24,
        "axes.labelsize": 24,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
    }):
        for key, parameters in plot_parameters.items():

            corner_kwargs = dict(
                levels=(1 - np.exp(-0.5), 1 - np.exp(-2), 1 - np.exp(-9 / 2.)),
                label_kwargs=dict(fontsize=24),
                bins=32,
            )

            samples.plot(
                parameters=parameters,
                labels=[release] + labels,
                colors=["C1", "C0", "C2"],
                type="corner",
                **corner_kwargs,
            )
            axs = np.array(plt.gcf().get_axes(), dtype=object).reshape(
                len(parameters), len(parameters)
            )

            for i, parameter in enumerate(parameters):
                jsd_base_e = samples.js_divergence(parameter)
                jsd_base_2 = jsd_base_e / np.log(2) * 1000
                print(f"{parameter}: {jsd_base_2} mbits")
                axs[i, i].set_title(f"{jsd_base_2:.2f} mbits", fontsize=20)
            plt.savefig(output / f"{args.SID}_{key}.{args.extension}", bbox_inches="tight")


if __name__ == "__main__":
    main()
