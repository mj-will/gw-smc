import copy
import numpy as np
from scipy.special import i0

from pesummary.utils.bounded_1d_kde import (
    ReflectionBoundedKDE,
    BoundedKDE,
    TransformBoundedKDE,
)


def vonmises_kernel(x, mu, kappa):
    """Von Mises kernel for KDEs"""
    return np.exp(kappa*np.cos(x-mu)).sum(1)/(2*np.pi*i0(kappa))

class PeriodicBoundedKDE:
    """Periodic KDE with von Mises kernel.
    
    Note: does not support bandwidth selection.
    """

    def __init__(self, pts, *, xlow, xhigh, kappa=10.0):
        self.pts = pts
        self.kappa = kappa
        self.xlow = xlow
        self.xhigh = xhigh
        self.pts_scale = self.scale(pts)

    def scale(self, x):
        return (2 * np.pi * (x - self.xlow) / (self.xhigh - self.xlow)) - np.pi

    def __call__(self, bins):
        x = self.scale(np.linspace(self.xlow, self.xhigh, len(bins)))
        kde = vonmises_kernel(x[:, None], self.pts_scale, self.kappa)
        kde /= np.trapz(kde, x=bins)
        return kde


known_kdes = {
    "reflective": ReflectionBoundedKDE,
    "transform": TransformBoundedKDE,
    "periodic": PeriodicBoundedKDE,
}


def fit_kde(
    samples,
    boundary_type=None,
    lower_bound=None,
    upper_bound=None,
    bw_method="silverman",
    **kwargs,
):
    """Fit a KDE to the given samples.
    
    If the boundary type is not specified, it will be inferred from the
    lower and upper bounds.
    """
    if boundary_type is None and not any(b is None for b in [lower_bound, upper_bound]):
        boundary_type = "reflective"

    if boundary_type not in known_kdes:
        raise ValueError(f"Unknown boundary type: {boundary_type}")
    KDEClass = known_kdes.get(boundary_type, BoundedKDE)

    if boundary_type != "periodic":
        kwargs["bw_method"] = bw_method

    kde = KDEClass(
        samples,
        xlow=lower_bound,
        xhigh=upper_bound,
        **kwargs
    )
    return kde
