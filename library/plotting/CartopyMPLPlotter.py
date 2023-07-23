import io
import base64
from dataclasses import dataclass

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import wrf

from app.WrfOutManager import WrfOutManager

matplotlib.use('WebAgg')


@dataclass
class PlotKwargs:
    contour_data: np.ndarray
    contour_kwargs: dict

    contour_fill_data: np.ndarray
    contour_fill_kwargs: dict

    quiver_data: np.ndarray = None
    quiver_kwargs: dict = None


class CartopyMplPlotter:

    def __init__(self, wrf_data_manager: WrfOutManager) -> None:
        self.data_manager = wrf_data_manager

        self._default_proj_transformer: ccrs.Projection = ccrs.PlateCarree()
        self._figure: plt.Figure = None
        self._ax: matplotlib.projections.GeoAxes = None
        self.lats = None
        self.lons = None

    def create_figure(self, **mpl_fig_kwargs) -> None:
        self._figure = plt.figure(figsize=self.data_manager.get_figure_size(), **mpl_fig_kwargs)

        projection_data = self.data_manager.extract_projection_and_bounds()
        self._ax = plt.axes(projection=projection_data["projection"])
        self._figure.set_facecolor("#e4ede8")
        self.lats, self.lons = self.data_manager.get_latitudes_and_longitudes()

        x_lim = projection_data["x-limit"]
        y_lim = projection_data["y-limit"]
        # margin = 200000
        # self._ax.set_xlim([x_lim[0] - margin, x_lim[1] + margin])
        # self._ax.set_ylim([y_lim[0] - margin, y_lim[1] + margin])

        self._ax.set_xlim(x_lim)
        self._ax.set_ylim(y_lim)
        self._ax.coastlines("10m", linewidth=0.8)

    def plot_slp(self, time_step: int = 0):
        slp_var = self.data_manager.get_slp(timeidx=time_step)
        # levels = np.arange(940, 1051, 1)
        ct = self._ax.contour(
            self.lons, self.lats,
            slp_var,
            # levels,
            linewidths=2, colors="black", alpha=0.8, fmt="%d",
            transform=self._default_proj_transformer,
        )
        self._ax.clabel(ct, inline=True, fontsize=8)
        return ct

    def plot_wind(self, time_step: int = 0, grid_interval: int = 25):
        u_wind, v_wind = self.data_manager.get_10m_winds(timeidx=time_step)
        self._ax.barbs(
            self.lons[::grid_interval, ::grid_interval],
            self.lats[::grid_interval, ::grid_interval],
            u_wind[::grid_interval, ::grid_interval],
            v_wind[::grid_interval, ::grid_interval],
            transform=self._default_proj_transformer,
            length=6)

    def plot_contour_fill(self, data_key: str, timeidx: int = 0):
        data_to_plot = self.data_manager.get_contour_fill_data(data_key, timeidx=timeidx)
        self._ax.set_title(f"Filled: {data_key}")
        if not data_to_plot.any() > 0:
            return
        # TODO: add better color map selection for variable
        cmap = "rainbow" if not data_key == "rh2" else "winter_r"
        ctf = self._ax.contourf(
            self.lons, self.lats,
            data_to_plot,
            cmap=cmap,
            transform=self._default_proj_transformer
        )
        plt.colorbar(ctf, ax=self._ax, shrink=.8)

    @staticmethod
    def __show_all_figures():
        plt.show()

    def clear_figure(self):
        self._figure.clear()

    def save(self) -> str:
        tmp_image = io.BytesIO()
        self._figure.tight_layout()
        self._figure.savefig(tmp_image, format='png')
        encoded = base64.b64encode(tmp_image.getvalue()).decode('utf-8')
        image_source = f'data:image/png;base64,{encoded}'
        return image_source
