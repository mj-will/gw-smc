# gw-smc

Validating Sequential Monte Carlo for Gravitational-wave Inference

pocomc version: 1.2.2
pocomc-bilby commit: 6426817080ba0082e9c34f9ebf4b9e3a3d09c1af 


## Experiments

Experiments are divided into those run on simulated data and those run on
real data.

All experiments so far use `bilby_pipe` to run the jobs. Jobs are started by
running

```
bilby_pipe <ini file>.ini --submit
```

Note: you may need to change some settings to make things run on e.g. a slurm
cluster.


## Install the utils package

This repo also contains a small utilities package to help producing results and plots. It can be installed by running

```
pip install .
```
