from dataclasses import dataclass
from functools import cached_property
from typing import List, Union, Dict

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from library.plotting.nclcmaps import get_ncl_cmap, create_ncl_cmap_with_linear_segmentation


# Try to provide an interface for the plot...
class Cmap:
    def __init__(self,
                 name: str,
                 ncl_cmap_name: str,
                 type: str,
                 cbar_extend: str = "neither",
                 **kwargs) -> None:
        self.name = name
        self.type = type
        self.ncl_cmap_name = ncl_cmap_name
        self.cbar_extend = cbar_extend
        if type == "uniform":
            self.vmin = kwargs["vmin"]
            self.vmax = kwargs["vmax"]
            self.interval = kwargs["interval"]
            self._ctf_kwargs = self._create_perceptually_uniform_colormap()
        elif type == "bounded":
            self.bounds = kwargs["bounds"]
            self._ctf_kwargs = self._create_boundary_normed_cmap()

    def __repr__(self):
        return f"<Cmap {self.name}>"

    @property
    def levels(self):
        if self.type == "uniform":
            return np.arange(self.vmin, self.vmax, self.interval)
        else:
            return self.bounds

    def create_cmap(self) -> Dict:
        return self._ctf_kwargs

    def _create_boundary_normed_cmap(self):
        cmap = get_ncl_cmap(self.ncl_cmap_name)
        norm = mcolors.BoundaryNorm(self.bounds, cmap.N)
        return {"norm": norm, "cmap": cmap, "levels": self.levels, "extend": self.cbar_extend}

    def _create_perceptually_uniform_colormap(self):
        n_bins = (self.vmax - self.vmin) / self.interval  # Number of discrete colors in the colormap
        cmap = create_ncl_cmap_with_linear_segmentation(name=self.name, ncl_cmap_name=self.ncl_cmap_name, n_bins=n_bins)
        return {"cmap": cmap, "levels": self.levels, "vmin": self.vmin, "vmax": self.vmax, "extend": self.cbar_extend}


@dataclass
class CTVariable:
    var_key: str
    title: str
    unit_text: str
    data_to_plot: np.ndarray = None

    def calculate_levels(self, interval: int) -> [int]:
        min_val = self.data_to_plot.min().data.item()
        max_val = self.data_to_plot.max().data.item()
        range_start = int(min_val - 2) if min_val % 2 == 0 else int(min_val - 1)
        range_end = int(max_val + 2) if max_val % 2 == 0 else int(max_val + 1)
        levels = np.arange(range_start, range_end, 2)
        return levels


@dataclass
class CTFVariable:
    var_key: str
    title: str
    unit_text: str
    cmap: Cmap
    data_to_plot: np.ndarray = None

    @cached_property
    def levels(self) -> [int]:
        if self.cmap.type == "uniform":
            return np.arange(self.cmap.vmin, self.cmap.vmax + 1, self.cmap.interval)
        else:
            return self.cmap.bounds
