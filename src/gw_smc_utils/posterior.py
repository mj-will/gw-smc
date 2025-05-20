import h5py


def load_bilby_posterior(filename: str, keys: list[str] = None):
    """Load just the posterior from a bilby hdf5 result object."""
    posterior = {}
    with h5py.File(filename, "r") as hdf_file:
        if keys is None:
            keys = hdf_file["posterior"].keys()
        for key in keys:
            if key not in hdf_file["posterior"]:
                print(f"Key {key} not found in posterior")
            else:
                posterior[key] = hdf_file[f"posterior/{key}"][()]
    return posterior
