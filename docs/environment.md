# Environment

We provide a `YAML` file to create a suitable environment using `conda`.

```{note}
For instructions on how to install `conda`, see the [`conda` documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).
```

The environment can be created using

```
conda env create -f environment.yml
```

and then activated using

```
conda activate gw-smc
```

## Installing gw-smc-utils

We also include a small utilities package that is used in some of the analyses and
when producing plots. This should be installed automatically when creating
the environment.

Alternatively, you can install it after having cloned the repository using `pip`:

```console
pip install .
```
