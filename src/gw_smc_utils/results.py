import pathlib


def find_gwtc_results(
    data_release_path,
    data_releases,
    event,
    cosmo,
):
    for release in data_releases:
        if cosmo:
            suffix = "cosmo"
        else:
            suffix = "nocosmo"
        release_path = pathlib.Path(f"{data_release_path}/{release}/")
        if not release_path.exists():
            raise RuntimeError(f"Release path {release_path} does not exist")
        matches = list(release_path.glob(f"*-{event}_*{suffix}.h5"))
        if len(matches) > 1:
            raise RuntimeError("Found more than one file")
        elif len(matches) == 0:
            continue
        else:
            filepath = matches[0]
            break
    else:
        raise RuntimeError("No file found")
    return filepath, release
