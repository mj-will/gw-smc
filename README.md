# Validating Sequential Monte Carlo for Gravitational-wave Inference

This repository contains code to reproduce all the of analyses described in
*Validating Sequential Monte Carlo for Gravitational-wave Inference*.

**Note: this repo is still being updated**

## Code versions:

Experiments were run using the following code versions:

- [`pocomc`@1074b20](https://github.com/minaskar/pocomc/commit/1074b20a8ffad00d03430eb2643fe839ad7360f6)
- `pocomc-bilby`@v0.1.0


### The utils package

This repo also contains a small utilities package called `gw-smc-utils` to help producing results and plots. It can be installed by running

```
pip install .
```

## Experiments

Experiments are divided into those run on simulated data and those run on
real data and all the relevant files are in the `experiments` directory.

## Useful links

- [Data release]()
- [pocomc documentation](https://pocomc.readthedocs.io/)
