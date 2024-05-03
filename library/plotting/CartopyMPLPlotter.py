import io
import base64

from dataclasses import dataclass

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import app.map.constants as Constants

from app.WrfOutManager import WrfOutManager
from app.map.models import CTFVariable, CTVariable

matplotlib.use('WebAgg')


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
        self._left_subtitle += f"{self.data_manager.data.title}\n"

        self._right_subtitle += f"GFS INPUT FROM: {self.data_manager.data.simulation_start_date}\nValid for: {date} UTC"

    def plot_contour(self, data_key: str, time_step: int = 0, level: [int] = None, line_color: str = "black",
                     line_style: str = "solid", cmap=None, line_width = 2):

        contour_var: CTVariable = self.data_manager.get_contour_data(key=data_key, timeidx=time_step)
        if contour_var is None:
            pass

        if level is not None:
            contour_var.levels = level

        if cmap:
            line_color = None

        self._left_subtitle += f" - {contour_var.title} {contour_var.unit_text}"

        ct = self._ax.contour(
            self.lons, self.lats,
            contour_var.data_to_plot,
            levels=contour_var.levels,
            linewidths=2, colors=line_color, alpha=0.8,
            transform=self._default_proj_transformer,
            zorder=5,
            linestyles=line_style,
            cmap=cmap
        )
        self._ax.clabel(ct, inline=True, fontsize=12)
        return ct

    def plot_figure_title(self, additional_msg: str = "", **kwargs):
        self._left_subtitle += additional_msg

        # if self._left_subtitle
        self._ax.set_title(self._right_subtitle, loc="right", fontdict={"size": 13})
        self._ax.set_title(self._left_subtitle, loc="left", fontdict={"size": 13})

    def plot_wind(self, wind_variable_key: str, time_step: int = 0, grid_interval: int = 25):
        u_wind, v_wind = self.data_manager.get_winds(key=wind_variable_key, timeidx=time_step)

        if wind_variable_key == Constants.FIELD_KEY_WS300:
            self._ax.streamplot(
                self.lons[::grid_interval, ::grid_interval],
                self.lats[::grid_interval, ::grid_interval],
                u_wind[::grid_interval, ::grid_interval],
                v_wind[::grid_interval, ::grid_interval],
                transform=self._default_proj_transformer, zorder=10, color="black", arrowsize=1.5, density=[.9, .9])

        elif wind_variable_key == Constants.FIELD_KEY_TEMP850:
            self._ax.barbs(
                self.lons[::grid_interval, ::grid_interval],
                self.lats[::grid_interval, ::grid_interval],
                u_wind[::grid_interval, ::grid_interval],
                v_wind[::grid_interval, ::grid_interval],
                transform=self._default_proj_transformer,
                length=6, zorder=10)
        elif wind_variable_key == Constants.FIELD_KEY_RH700:
            self._ax.barbs(
                self.lons[::grid_interval, ::grid_interval],
                self.lats[::grid_interval, ::grid_interval],
                u_wind[::grid_interval, ::grid_interval],
                v_wind[::grid_interval, ::grid_interval],
                transform=self._default_proj_transformer,
                length=6, zorder=10)
        else:
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
