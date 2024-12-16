import numpy as np
from scipy.special import i0, iv
from pesummary.utils.bounded_1d_kde import (
    ReflectionBoundedKDE,
    BoundedKDE,
    TransformBoundedKDE,
)


def vonmises_kernel(x: np.ndarray, mu: np.ndarray, nu: float):
    """Von Mises kernel for KDEs"""
    return np.exp(nu*np.cos(x-mu)).sum(1)/(2*np.pi*i0(nu))


def estimate_kappa(angles, kappa_range, n_points: int = 100):
    """Estimate the kappa parameter for a von Mises distribution.

    Based on the method described in Section 3 of:
    https://www.sciencedirect.com/science/article/pii/S0167947307004367?ref=cra_js_challenge&fr=RR-1
    """
    kappa = np.linspace(kappa_range[0], kappa_range[1], n_points)[:, np.newaxis]
    mu_k = np.arctan2(
        np.sum(np.sin(kappa * angles), axis=1),
        np.sum(np.cos(kappa * angles), axis=1),
    )[:, np.newaxis]
    assert len(mu_k) == n_points
    mle = np.mean(np.cos(kappa * angles - mu_k), axis=1)
    # Find the nu that minimizes the MISE proxy
    optimal_kappa = kappa[np.argmin(mle)]
    return optimal_kappa


class PeriodicBoundedKDE:
    """Periodic KDE with von Mises kernel.

    Supports the bandwidth selection method described in Section 3 of
    https://www.sciencedirect.com/science/article/pii/S0167947307004367?ref=cra_js_challenge&fr=RR-1
    """

    def __init__(
        self,
        pts,
        *,
        xlow,
        xhigh,
        kappa=None,
        estimate_bandwidth=True,
        bandwidth_method="taylor",
        kappa_range=(0, 100),
        n_kappa_points=500,
    ):
        self.pts = pts
        self.kappa = kappa
        self.xlow = xlow
        self.xhigh = xhigh
        self.pts_scale = self.scale(pts)
        self._n = 2
        self.bandwidth_method = bandwidth_method
        if not estimate_bandwidth and kappa is None:
            raise ValueError(
                "kappa must be provided if estimate_bandwidth is False"
            )
        self.kappa = (
            kappa
            or estimate_kappa(self.pts_scale, kappa_range, n_kappa_points)
        )
        self.nu = self.bandwidth(self.kappa)

    def bandwidth(self, k):
        # These methods are based on the implementation in R's vmkde
        if self.bandwidth_method == "rot":
            return (
                (k * self._n * (2 * iv(1, 2 * k) + 3 * k * iv(2, 2 * k)))
                / (4 * np.pi**0.5 * iv(0, k)**2)
            )**0.4
        elif self.bandwidth_method == "taylor":
            return ((3 * self._n * k**2 * iv(2, 2 * k)) / (4 * np.pi**0.5 * iv(0, k)**2))**0.4
        else:
            raise ValueError(f"Unknown bandwidth method: {self.bandwidth_method}")

    def scale(self, x):
        return (2 * np.pi * (x - self.xlow) / (self.xhigh - self.xlow)) - np.pi

    def __call__(self, bins):
        x = self.scale(np.linspace(self.xlow, self.xhigh, len(bins)))
        kde = vonmises_kernel(x[:, None], self.pts_scale, self.nu)
        kde /= np.trapz(kde, x=bins)
        return kde

    def evaluate(self, x):
        return self(x)


known_kdes = {
    "reflective": ReflectionBoundedKDE,
    "transform": TransformBoundedKDE,
    "periodic": PeriodicBoundedKDE,
    "none": BoundedKDE,
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
