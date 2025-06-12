# Binary black hole analyses

## Reproducing the figures

We include notebooks to reproduce the figures in the paper:

- [P-P plots](./plotting/pp_plot.ipynb)
- [Jensen-Shannon Divergence plot](./plotting/pp_test_jsd.ipynb)
- [Comparison plots](./plotting/pp_test_comparison.ipynb)

Each notebooks includes explanations about how the plots are made.
Running these requires you to have created a [suitable environment](./environment) and
downloaded the [core data release](./data_release).

## Running the analyses

Alternatively, if you wish to run the analyses directly, we include all the scripts to do so
in `experiments/simulated_data/pp_tests/`.

```{note}
The scripts provided include various paths that will need updating in order to run on your system.
They also assume that you have access to a system with HTCondor configured.
```

### Data

Before running the analyses you must either download the data from the data release
or generate your own data. If you aim to reproduce the exact analyses, we recommend downloading
the data since random number generation mary vary between systems.

#### Using data from the data release

The data used to produce the results in the paper is included the data release, see [data release](./data_release)
for instructions on how to download the data.

#### Generating new data

We also include scripts for generating new data in `experiments/simulated_data/pp_test/data`. This
includes the following scripts:

- `generate_injections.py`: this script generates the injection parameters
- `make_frames.py`: this script generates the frame files (`.hdf5`) for each injection (and each detector)
- `generate_data.sh`: this bash script calls above scripts and was used to generate the exact injections used in the paper.

### Submitting the analyses

Since we're not using `bilby_pipe`'s built-in functionality for performing P-P tests,
we use a custom script to construct a 'superdag' that submits a DAG for each injection.

The settings for the analyses are defined in the two template ini files provided:

- `dynesty_template.ini`
- `pocomc_template.ini`

Before submitting the analyses, make sure the paths in these files point to the correct locations.

For simplicity, we include a script (`submit.sh`) that can be edited to submit the relevant job:

```bash
#!/usr/bin/env bash
SAMPLER=pocomc
LABEL=2det
python \
    generate_super_dag.py \
    ${SAMPLER}_template.ini \
    --outdir outdir_${SAMPLER}_${LABEL}/ \
    --injection-file data/bbh_injections_uniform_chirp_mass.hdf5 \
    --data-dir data/injections/uniform_chirp_mass_mass_ratio/ \
    --n-injections 100 \
    --prior-file bbh_priors.prior \
    --superdag-name superdag_$SAMPLER \
    --detectors H1 L1 \
    --detector-frame \
    --submit
```

Change `SAMPLER`, `LABEL` and `detectors` to configure the exact the sampler
that is used, the label for the run and which detectors are used.

You will also need to change the paths for `--injection-file` and `--data-dir`
to point to the correct paths. If you've downloaded the data release, then this
will be the file called `pp_test_injection_file.hdf5` and the `pp_test_injection_data`
directory.

Once the script is run, the output directory will contain one directory per
injection (produced by `bilby_pipe`)


### Computing the Jensen-Shannon divergence

The `compute_js.py` script is used to compute the Jensen-Shannon divergence
between the various runs. For simplicity we also include an HTCondor submit
file that can be used to run the script for all 100 injections.

As before, this will need updating to point to correct paths:

```
accounting_group = ligo.dev.o4.cbc.pe.bilby
accounting_group_user = michael.williams

# Change this to set the number of CPUs
ncpus=4

# Change these to select the input directories
# The should match what was used in `submit.sh`
ndets=3
dets=H1L1V1
frame=det
# Make sure the labels match the labels used for the runs
dynesty_label=uniform_chirp_mass
pocomc_label=uniform_chirp_mass_transforms_sinf

filename=jsd_results/update_data/uniform_chirp_mass_transforms_sinf/$(frame)_frame/$(ndets)det_max_min_xsteps/data$(ProcId).json
result1=outdir_dynesty_$(ndets)det_$(frame)_frame_$(dynesty_label)/injection_$(ProcId)/final_result/dynesty_pp_test_data0_1364342674-0_analysis_$(dets)_result.hdf5
result2=outdir_pocomc_$(ndets)det_$(frame)_frame_$(pocomc_label)/injection_$(ProcId)/final_result/pococmc_pp_test_data0_1364342674-0_analysis_$(dets)_result.hdf5

executable   = /home/michael.williams/.conda/envs/gw-smc-sinf/bin/python
arguments    = compute_js.py $(result1) $(result2) --filename $(filename) --verbose --n-pool $(ncpus) --n-samples 5000 --n-tests 10 --xsteps 1000

output       = condor_logs/jsd_$(ClusterId).$(ProcId).out
error        = condor_logs/jsd_$(ClusterId).$(ProcId).err
log          = condor_logs/jsd_$(ClusterId).$(ProcId).log

request_cpus   = $(ncpus)
request_memory = 1024M
request_disk   = 1024M

should_transfer_files = no

queue 100
```


### Producing plots for custom analyses

We include scripts for producing plots similar to those in the paper for your
own analyses.

### P-P plots

P-P plots can be made using the `pp_test.py` script in this directory. The basic usage is:

```
python pp_test.py \
    --result-dir <path/to/result/directory> \
    --injection-file <path/to/injection/file/
    --figure-format png \
    --filename pp_test_pocomc_3det \
    --outdir figures
```

#### Jensen-Shannon divergence plots

Once the JS divergences have been computed, the results are stored in a `JSON`
file per injection. The [JSD plotting notebooks](./plotting/pp_test_jsd.ipynb)
shows how to load and plot the results.
