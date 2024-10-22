import h5py


def load_bilby_posterior(filename: str, keys: list[str] = None):
    """Load just the posterior from a bilby hdf5 result object."""
    posterior = {}
    with h5py.File(filename, "r") as hdf_file:
        if keys is None:
            keys = hdf_file[f"posterior"].keys()
        for key in keys:
            posterior[key] = hdf_file[f"posterior/{key}"][()]
    return posterior
