import h5py
import numpy as np
from scipy.special import erfc, erfcinv


def gaussian_cdf(x):
    """Gaussian CDF with log-Jacobian determinant"""
    log_j = -0.5 * np.log(2 * np.pi) - 0.5 * (x**2.0)
    x = 0.5 * erfc(-x / np.sqrt(2.0))
    return x, log_j


def inverse_gaussian_cdf(x):
    """Inverse Gaussian CDF with log-Jacobian determinant"""
    x = -np.sqrt(2) * erfcinv(2.0 * x)
    log_j = 0.5 * np.log(2 * np.pi) + 0.5 * (x**2.0)
    return x, log_j


def get_bilby_prior(filename: str):
    from bilby.gw.prior import CBCPriorDict
    import json

    with h5py.File(filename, "r") as hdf_file:
        priors_dict = json.loads(hdf_file["priors"][()])
        priors = CBCPriorDict._get_from_json_dict(priors_dict)
    return priors
