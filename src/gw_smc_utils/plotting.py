import importlib

import matplotlib.pyplot as plt
import numpy as np


def set_style() -> None:
    """Set the plotting style"""
    with importlib.resources.path("gw_smc_utils", "paper.mplstyle") as p:
        plt.style.use(p)


def lighten_colour(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Copied from: https://gist.github.com/ihincks/6a420b599f43fcd7dbd79d56798c4e5a
    
    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = np.array(colorsys.rgb_to_hls(*mc.to_rgb(c)))
    return colorsys.hls_to_rgb(c[0],1-amount * (1-c[1]),c[2])