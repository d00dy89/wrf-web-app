import numpy as np
import matplotlib.colors as mcolors

from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from library.plotting.ncl_colors import colors


def get_ncl_cmap(name: str) -> ListedColormap:
    data = np.array(colors[name])
    data = data / np.max(data)
    cmap = ListedColormap(data, name=name)
    return cmap


def create_ncl_cmap_with_linear_segmentation(name: str, ncl_cmap_name: str, n_bins: int) -> LinearSegmentedColormap:
    data = np.array(colors[ncl_cmap_name])
    data = data / np.max(data)
    cmap = LinearSegmentedColormap.from_list(name, data, n_bins)
    return cmap

