"""
Code to calculate the JS divergence between samples.

Based on the code used in https://doi.org/10.5281/zenodo.8124198
"""

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


def calculate_js(
    samplesA,
    samplesB,
    ntests=10,
    xsteps=1000,
    nsamples=1000,
    base=2,
    rng=None,
    bw_method="silverman",
    **kwargs,
):

    js_array = np.zeros(ntests)
    if nsamples is None:
        nsamples = min(len(samplesA), len(samplesB))

    if rng is None:
        rng = np.random.default_rng()

    for j in range(ntests):
        samples_a = rng.choice(samplesA, size=nsamples, replace=False)
        samples_b = rng.choice(samplesB, size=nsamples, replace=False)
        xmin = max(np.min(samples_a), np.min(samples_b))
        xmax = min(np.max(samples_a), np.max(samples_b))
        x = np.linspace(xmin, xmax, xsteps)
        A_pdf = fit_kde(samplesA, bw_method=bw_method, **kwargs).evaluate(x)
        B_pdf = fit_kde(samplesB, bw_method=bw_method, **kwargs).evaluate(x)

        js_array[j] = np.nan_to_num(np.power(jensenshannon(A_pdf, B_pdf, base=base), 2))

    return calc_median_error(js_array)
