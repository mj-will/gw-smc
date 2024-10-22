import importlib

import matplotlib.pyplot as plt


def set_style() -> None:
    """Set the plotting style"""
    with importlib.resources.path("gw_smc_utils", "paper.mplstyle") as p:
        plt.style.use(p)
