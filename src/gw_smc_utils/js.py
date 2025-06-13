"""
Code to calculate the JS divergence between samples.

Based on the code used in https://doi.org/10.5281/zenodo.8124198
"""

from functools import partial
from itertools import starmap

import numpy as np
from scipy.spatial.distance import jensenshannon


from .kde import fit_kde


def calc_median_error(jsvalues, quantiles=(0.16, 0.84)):
    quants_to_compute = np.array([quantiles[0], 0.5, quantiles[1]])
    quants = np.percentile(jsvalues, quants_to_compute * 100)
    median = quants[1]
    plus = quants[2] - median
    minus = median - quants[0]
    return median, plus, minus


def _compute_js(samplesA, samplesB, xsteps=1000, base=2, **kwargs):
    xmin = max(np.min(samplesA), np.min(samplesB))
    xmax = min(np.max(samplesA), np.max(samplesB))
    x = np.linspace(xmin, xmax, xsteps)
    A_pdf = fit_kde(samplesA, **kwargs)(x)
    B_pdf = fit_kde(samplesB, **kwargs)(x)
    return np.nan_to_num(np.power(jensenshannon(A_pdf, B_pdf, base=base), 2))


def calculate_js(
    samplesA,
    samplesB,
    n_tests=10,
    xsteps=1000,
    n_samples=1000,
    base=2,
    rng=None,
    verbose=False,
    pool=None,
    **kwargs,
):
    min_samples = min(len(samplesA), len(samplesB))
    if n_samples is None:
        n_samples = min_samples
        if verbose:
            print(f"Using all samples ({n_samples})")
    elif n_samples > min_samples:
        print(
            "Warning: n_samples is greater than the number of samples in one of the datasets. Using all samples."
        )
        print(f"Samples A = {len(samplesA)}, Samples B = {len(samplesB)}")
        n_samples = min_samples

    if rng is None:
        rng = np.random.default_rng()

    if pool is not None:
        map_fn = pool.starmap
    else:
        map_fn = starmap

    samples_a = np.array(
        [rng.choice(samplesA, size=(n_samples), replace=False) for _ in range(n_tests)]
    )
    samples_b = np.array(
        [rng.choice(samplesB, size=(n_samples), replace=False) for _ in range(n_tests)]
    )

    map_kwargs = kwargs.copy()
    map_kwargs["xsteps"] = xsteps
    map_kwargs["base"] = base

    js_vals = list(
        map_fn(partial(_compute_js, **map_kwargs), zip(samples_a, samples_b))
    )
    return js_vals
