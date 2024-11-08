import KDEpy
import numpy as np

from .utils import gaussian_cdf, inverse_gaussian_cdf


class BaseBoundedKDEMixin:
    """Mixin that adds support for boundaries"""

    def evaluate(self, data):
        data, log_abs_det = self.transform(data)
        return np.exp(np.log(super().evaluate(data)) + log_abs_det)

    def fit(self, samples, lower_bound=None, upper_bound=None, weights=None, eps=None):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        if eps:
            self.lower_bound -= eps
            self.upper_bound += eps
        samples, _ = self.transform(samples)
        return super().fit(samples, weights=weights)

    def transform(self, samples):
        return samples, np.zeros_like(samples)

    def inverse_transform(self, samples):
        return samples, np.zeros_like(samples)


class UnitIntervalKDEMixin(BaseBoundedKDEMixin):

    def transform(self, samples):
        samples = (samples - self.lower_bound) / (self.upper_bound - self.lower_bound)
        log_abs_det = -np.sum(
            np.log(self.upper_bound - self.lower_bound)
        ) * np.ones_like(samples)
        return samples, log_abs_det

    def inverse_transform(self, samples):
        samples = samples * (self.upper_bound - self.lower_bound) + self.lower_bound
        log_abs_det = np.sum(
            np.log(self.upper_bound - self.lower_bound)
        ) * np.ones_like(samples)
        return samples, log_abs_det


class BoundedKDEMixin(UnitIntervalKDEMixin):

    def transform(self, samples):
        samples, log_abs_det = super().transform(samples)
        samples, log_abs_det_gauss = inverse_gaussian_cdf(samples)
        return samples, log_abs_det + log_abs_det_gauss

    def inverse_transform(self, samples):
        samples, log_abs_det_gauss = gaussian_cdf(samples)
        samples, log_abs_det = super().inverse_transform(samples)
        return samples, log_abs_det + log_abs_det_gauss


class ReflectiveKDEMixin(BoundedKDEMixin):

    def transform(self, samples):
        if not self.lower_bound and not self.upper_bound:
            raise ValueError("Reflective KDE requires at least one boundary.")
        if self.lower_bound is not None:
            samples_out = np.concatenate([np.sort(2 * self.lower_bound - samples), samples])
        else:
            samples_out = samples.copy()

        if self.upper_bound:
            samples_out = np.concatenate([samples_out, np.sort(2 * self.upper_bound - samples)])

        return samples_out, np.zeros_like(samples_out)

    def inverse_transform(self, samples):
        if self.lower_bound:
            samples[samples < self.lower_bound] = (
                2 * self.lower_bound - samples[samples < self.lower_bound]
            )
        if self.upper_bound:
            samples[samples > self.upper_bound] = (
                2 * self.upper_bound - samples[samples > self.upper_bound]
            )
        return samples, np.zeros_like(samples)

    def evaluate(self, data):
        y = super().evaluate(data)
        y_split = y.reshape(-1, len(data))
        return y_split.sum(0)


class PeriodicKDEMixin(BaseBoundedKDEMixin):

    def transform(self, samples):
        samples = np.concatenate(
            [
                samples - (self.upper_bound - self.lower_bound),
                samples,
                samples + (self.upper_bound - self.lower_bound),
            ]
        )
        return samples, np.zeros_like(samples)

    def inverse_transform(self, samples):
        samples = samples % (self.upper_bound - self.lower_bound) + self.lower_bound
        return samples, np.zeros_like(samples)

    def evaluate(self, data):
        y = super().evaluate(data)
        y_split = y.reshape(-1, len(data))
        return y_split.sum(0)


def get_mixin(boundary_type):
    if boundary_type == "unit":
        return UnitIntervalKDEMixin
    elif boundary_type == "bounded":
        return BoundedKDEMixin
    elif boundary_type == "reflective":
        return ReflectiveKDEMixin
    elif boundary_type == "periodic":
        return PeriodicKDEMixin
    else:
        return BaseBoundedKDEMixin


def fit_kde(
    samples,
    kde_class="NaiveKDE",
    boundary_type=None,
    lower_bound=None,
    upper_bound=None,
    eps=None,
    verbose: bool = False,
    **kwargs,
):
    """Fit a KDE to the given samples"""
    try:
        BaseKDEClass = getattr(KDEpy, kde_class)
    except AttributeError:
        raise ValueError(f"Invalid KDE class: {kde_class}.")

    if verbose:
        print(f"Using {BaseKDEClass} KDE class")

    if boundary_type is None and not any(b is None for b in [lower_bound, upper_bound]):
        boundary_type = "reflective"

    MixinClass = get_mixin(boundary_type)

    class KDEClass(MixinClass, BaseKDEClass):
        pass

    if verbose:
        print(f"Using {MixinClass} mixin")
        if lower_bound:
            print(f"Lower bound: {lower_bound}")
        if upper_bound:
            print(f"Upper bound: {upper_bound}")

    kde = KDEClass(**kwargs)
    
    return kde.fit(
        samples, lower_bound=lower_bound, upper_bound=upper_bound, eps=eps
    )
