# Binary neutron star analyses

## Reproducing the figures

We include a notebook to reproduce the figures and tables for the BNS analyses:

- [BNS Results](./plotting/bns_results)

Running this notebook requires you to have created a [suitable environment](./environment) and
downloaded the [core data release](./data_release).

## Running the analyses

Alternatively, if you wish to run the analyses directly, we include all the scripts to do so
in `experiments/simulated_data/bns/`.

```{note}
Running the analyses requires access to a system with HTCondor. Running on other systems
may be possible but will likely require modifying the scripts
```

### Downloading the ROQs

The BNS analyses all use ROQs to accelerate the likelihood calculation (see the paper for more details and references).
These need to be downloaded from Zenodo before any of the analyses can be run.

In particular, we use [this 128-second basis](https://zenodo.org/records/14279382/files/basis_128s.hdf5) which you
can either downloaded directly or using the script provided:

```console
bash fetch_roqs.sh
```

### Submitting jobs using `bilby_pipe`

The BNS analyses are run directly using `bilby_pipe`. The `experiments/simulated_data/bns/` directory contains ini files for all the combinations of samplers, spin and tidal parameters.

Each ini file can be submitted by running:

```
bilby_pipe <ini file> --submit
```

Alternatively, you can use the `Makefile` to submit all the jobs in parallel:

```
make submit_all
```

```{warning}
This does not check for existing analyses.
```

### Calculating the Jensen-Shannon Divergence

The `compute_js.py` can be used to compute the JSD for the various runs.

You can either use it directly:

```console
python compute_js.py --outdir jsd_results --samplers dynesty pocomc --n-pool 4 --prefix outdir
```

or using the `Makefile`

```
make compute_jsd
```


### Producing plots

We do not include specific scripts for producing figures from your own analyses,
instead we suggest modifying the notebook included in the data release: [BNS results](./plotting/bns_results).
