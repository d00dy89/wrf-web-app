from dataclasses import dataclass
from functools import cached_property
from typing import List, Union, Dict

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# Try to provide an interface for the plot...
class Cmap:
    def __init__(self, name: str, colors: Union[str, List[str]], type: str, **kwargs) -> None:
        self.name = name
        self.colors = self._extract_colors_from_named_cmap(colors) if isinstance(colors, str) else colors
        self.type = type
        if type == "uniform":
            self.vmin = kwargs["vmin"]
            self.vmax = kwargs["vmax"]
            self.interval = kwargs["interval"]
        elif type == "bounded":
            self.bounds = kwargs["bounds"]

    def __repr__(self):
        return f"<Cmap {self.name}>"

    @staticmethod
    def _extract_colors_from_named_cmap(cmap_name: str) -> List[str]:
        cmap = plt.get_cmap(cmap_name)
        return [mcolors.rgb2hex(rgba) for rgba in cmap(0.5)]

    def create_cmap(self) -> Dict:
        if self.type == "uniform":
            return self._create_perceptually_uniform_colormap()
        elif self.type == "bounded":
            return self._create_boundary_normed_cmap()

    def _create_boundary_normed_cmap(self):
        cmap = mcolors.ListedColormap(self.colors)
        norm = mcolors.BoundaryNorm(self.bounds, cmap.N)
        return {"norm": norm, "cmap": cmap}

    def _create_perceptually_uniform_colormap(self):
        n_bins = (self.vmax - self.vmin) / self.interval  # Number of discrete colors in the colormap
        cmap = mcolors.LinearSegmentedColormap.from_list(self.name, self.colors, N=n_bins)
        return {"cmap": cmap, "vmin": self.vmin, "vmax": self.vmax}


@dataclass
class CTVariable:
    var_key: str
    title: str
    unit_text: str
    data: np.ndarray = None

    def calculate_levels(self, interval: int) -> [int]:
        min_val = self.data.min().data.item()
        max_val = self.data.max().data.item()
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
