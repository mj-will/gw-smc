# Analyses with real data

## Producing plots

For these analyses, we provide a command line tool in `gw-smc-uitls` that produces the comparison plots.

Its basic usage is:

```
gw_smc_utils_plot_event \
    --results <path to GW-SMC data release>/real_data/GW200129_bilby_result_pocomc.hdf5 \
    --labels pocomc \
    --data-release-path <path to the GWTC data releases> \
    --SID GW200129 \
    --extension pdf
```

```{note}
The parameters are currently hardcoded. We recommend using `pesummary` if you
wish to explore more of the parameters.
See [the documentation](https://lscsoft.docs.ligo.org/pesummary/) for more details.
```

Alternatively, the `Makefile` in `plotting` includes commands to produces the plots (including automatically downloading the GWTC data releases). In the plotting directory run:

```
make GW150914_plots
```

or swap `GW150914` for `GW200129`.


### Results for GW150914

```{important}
These figures are generated automatically and may use different random number generation
compared to the results shown in the paper.
```

**Intrinsic parameters**
```{image} plotting/figures/GW150914_intrinsic.png
:alt: posterior distribution for GW150914 showing a subset of the intrinsic parameters.
```

**Extrinsic parameters**
```{image} plotting/figures/GW150914_localization.png
:alt: posterior distribution for GW150914 showing the localization parameters.
```

### Results for GW200129

```{important}
These figures are generated automatically and may use different random number generation
compared to the results shown in the paper.
```

**Intrinsic parameters**
```{image} plotting/figures/GW200129_intrinsic.png
:alt: posterior distribution for GW200129 showing a subset of the intrinsic parameters.
```

**Extrinsic parameters**
```{image} plotting/figures/GW200129_localization.png
:alt: posterior distribution for GW200129 showing the localization parameters.
```

## Running the analyses

`bilby_pipe` ini files for both the events we analyse are included in `experiments/real_data/<SID>`
where `SID` is either `GW150914` or `GW200129`.

### Fetching the PSDs

Having downloaded the data releases, the PSDs are fetching using the `fetch_psds`
command in the `Makefile`:

```
make fetch_psds
```

This will extract the PSDs from the GWTC data release files and save them to
`psds`

### Submitting the analyses

Each ini file can be submitted by running:

```
bilby_pipe <ini file> --submit
```

## Downloading the GWTC data release

To download the GWTC data releases used for producing plots and running analyses
run the following in the `gwtc_data_releases` directory of the repository:

```
make
```

This will only download the files that are necessary.
