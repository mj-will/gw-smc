# Analyzing real events

## Downloading GWTC 2.1 and 3 samples

This `Makefile` in this directory contains commands to download the data release
files needed to produce the comparison pages.

Run the following to download the files:

```bash
make data_releases
```

**Note:** if you have changed `DATA_RELEASE_PATH` the in `config.mk`, then you will need to change
`data_releases` to match.


## Producing plots

The figures included in the paper can be produced by running the following command in this directory:

```
make GW150914_plots GW200129_plots
```

The figures are saved in the `figures` directory.
