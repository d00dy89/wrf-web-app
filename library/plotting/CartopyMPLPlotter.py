import io
import base64

from dataclasses import dataclass

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from app.WrfOutManager import WrfOutManager
from app.map.models import CTFVariable

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
        self._left_subtitle: str = ""
        self._right_subtitle: str = ""
        self._ax: matplotlib.projections.GeoAxes = None
        self.lats = None
        self.lons = None

    def create_figure(self, **mpl_fig_kwargs) -> None:
        figsize = self.data_manager.get_figure_size()

        self._figure = plt.figure(figsize=figsize, **mpl_fig_kwargs)
        self._figure.set_facecolor("#e4ede8")

        self._left_subtitle = ""
        self._right_subtitle = ""

        projection_data = self.data_manager.extract_projection_and_bounds()
        self._ax = plt.axes(projection=projection_data["projection"])

        self.lats, self.lons = self.data_manager.get_latitudes_and_longitudes()

        x_lim = projection_data["x-limit"]
        y_lim = projection_data["y-limit"]
        # margin = 200000
        # self._ax.set_xlim([x_lim[0] - margin, x_lim[1] + margin])
        # self._ax.set_ylim([y_lim[0] - margin, y_lim[1] + margin])

        self._ax.set_xlim(x_lim)
        self._ax.set_ylim(y_lim)
        self._ax.coastlines("10m", linewidth=0.8)

    def plot_gridlines(self):
        # plot grid lines
        gl = self._ax.gridlines(
            crs=self._default_proj_transformer,
            draw_labels=True,
            x_inline=False,
            y_inline=False,
            linewidth=.9, color='black', alpha=0.8, linestyle='--')
        gl.right_labels = True
        gl.left_labels = False
        gl.top_labels = False
        gl.bottom_labels = True
        gl.xlabel_style = {'rotation': 0, "va": "center", "bbox": {"pad": 2}}
        gl.xpadding = 10
        # gl.ypadding = 0.2
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER

    def generate_figure_title(self, timeidx: int = 0):
        date = self.data_manager.get_time_string_by_index(timeidx)
        self._left_subtitle += f" GFS INPUT FROM: {self.data_manager.data.simulation_start_date}\n" \
                               f"{self.data_manager.data.title}"
        self._right_subtitle += f"Valid for: {date} UTC"

    def plot_contour(self, time_step: int = 0, line_color: str = "black"):
        # TODO: make it plot any other variable
        slp_var = self.data_manager.get_slp(timeidx=time_step)

        slp_min = slp_var.min().data.item()
        slp_max = slp_var.max().data.item()
        slp_start = int(slp_min - 2) if slp_min % 2 == 0 else int(slp_min - 1)
        slp_end = int(slp_max + 2) if slp_min % 2 == 0 else int(slp_max + 1)
        levels = np.arange(slp_start, slp_end, 2)

        ct = self._ax.contour(
            self.lons, self.lats,
            slp_var,
            levels=levels,
            linewidths=2, colors=line_color, alpha=0.8,
            transform=self._default_proj_transformer,
            zorder=5,
        )
        self._ax.clabel(ct, inline=True, fontsize=12)
        return ct

    def plot_figure_title(self, additional_msg: str = "", **kwargs):
        self._left_subtitle += additional_msg
        self._ax.set_title(self._right_subtitle, loc="right")
        self._ax.set_title(self._left_subtitle, loc="left")

    def plot_wind(self, time_step: int = 0, grid_interval: int = 25):
        u_wind, v_wind = self.data_manager.get_10m_winds(timeidx=time_step)
        self._ax.barbs(
            self.lons[::grid_interval, ::grid_interval],
            self.lats[::grid_interval, ::grid_interval],
            u_wind[::grid_interval, ::grid_interval],
            v_wind[::grid_interval, ::grid_interval],
            transform=self._default_proj_transformer,
            length=6, zorder=10)

    def plot_contour_fill(self, data_key: str, timeidx: int = 0):
        ctf_var: CTFVariable = self.data_manager.get_contour_fill_data(data_key, timeidx=timeidx)

        self._left_subtitle += f" - {ctf_var.title} {ctf_var.unit_text}"

        ctf_kwargs = ctf_var.cmap.create_cmap()

        ctf = self._ax.contourf(
            self.lons, self.lats,
            ctf_var.data_to_plot,
            # levels=ctf_var.levels,
            transform=self._default_proj_transformer,
            zorder=0,
            **ctf_kwargs,
        )
        cbar = plt.colorbar(ctf, ax=self._ax,
                            orientation="horizontal",
                            ticks=ctf_var.levels,
                            boundaries=ctf_var.levels,
                            pad=0.03, shrink=0.83,
                            extend=ctf_var.cmap.cbar_extend)

        cbar.set_label(f"{ctf_var.title} {ctf_var.unit_text}")

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
