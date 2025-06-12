# Data release

This page describes how to download the code and data releases.

## Code

The scripts for performing the analyses are available in this [Zenodo record]() and
on [GitHub](https://github.com/mj-will/gw-smc).

The GitHub repository can be clone by running:

```
git clone git@github.com:mj-will/gw-smc.git
```

### Structure

The code release contains the following directories:

- `data_release`: scripts for preparing and downloading the data release
- `gwtc_data_release`: scripts for download relevant files from the GWTC-2.1 and GWTC-3 data releases
- `experiments`: scripts for performing the analyses
- `plotting`: scripts and notebooks for reproducing the figures and tables in the paper
- `src`: the source code for the `gw_smc_utils` packages that contains common functions used in the different analyses and plotting
- `docs`: the code for producing the data release page

and some additional files for build the `gw_smc_utils` package and managing the repository.

## Results and data

The results and data are available in a separate [Zenodo record](). We recommend downloading
this using the scripts provided in the `data_release` directory the code data release.

This enables you to either download the entire release or only a fraction using the
`Makefile`:

- `make download_core`: download only the core results need to reproduce the figures and table
- `make download_additional`: download the additional results such as `bilby` result files
- `make download_data`: download the injection data used for the BBH analyses
- `make download_all`: download the entire release.

**Note:** the entire data release is several GBs and may take while to download.
