## bilby_pipe version

These analyses require the fix from https://git.ligo.org/lscsoft/bilby_pipe/-/merge_requests/584.
They therefore use the master branch at commit [d374c6a0264b27463fbedad31c22aa33f26ab99c](https://git.ligo.org/lscsoft/bilby_pipe/-/commit/d374c6a0264b27463fbedad31c22aa33f26ab99c).

This can be installed using `pip`:

```
pip install git+https://git.ligo.org/lscsoft/bilby_pipe.git@d374c6a0264b27463fbedad31c22aa33f26ab99c
```


## Authentication

```
kinit
export HTGETTOKENOPTS="-a vault.ligo.org -i igwn"
htgettoken
```


## Downloading GWTC 2.1 and 3 samples

**Note:** this will download more 40 GB of data and may take a long time.

First, install `zenodo_get`

```
pip install zenodo_get
```

then, for GWTC 2.1, run

```
zenodo_get https://doi.org/10.5281/zenodo.6513631
```

and for GWTC 3, run

```
zenodo_get https://doi.org/10.5281/zenodo.8177023
```