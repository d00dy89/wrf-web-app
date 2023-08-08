from typing import Tuple

import wrf

from netCDF4 import Dataset

from app.path_config import PathConfig
from library.models.WRFData import WRFData
from library.utils import Singleton

import app.map.constants as Constants
from app.map.models import CTFVariable


class WrfOutManager(metaclass=Singleton):

    def __init__(self, path_config: PathConfig) -> None:
        self.path_config = path_config
        # self.SHP_FOLDER = shape_file_folder
        self._dataset: Dataset = None
        self.data: WRFData = None

        self._current_time_idx: int = 0
        self._time_map: [dict] = None

    def read_dataset(self, from_file: str) -> None:
        file_path = self.path_config.WRF_OUTPUT_FOLDER_PATH.joinpath(from_file)
        try:
            print('Creating dataset from file: ', file_path)
            self._dataset = Dataset(file_path, mode='r')
            self.data = WRFData(self._dataset)

        except Exception as e:
            print(str(e))

    def close_dataset(self) -> bool:
        success = False
        try:
            self._dataset.close()
            self._dataset = None
            self.data = None
            self._current_time_idx = 0
            self._time_map = None
            success = True
            print('Closed Dataset!')
        except Exception as e:
            print(f'Exception closing netCDF4 dataset.\n{e}')
            return success

    def extract_projection_and_bounds(self) -> {}:
        return {
            "library": "cartopy",
            "projection": self.data.cartopy_proj,
            "y-limit": self.data.cartopy_ylim,
            "x-limit": self.data.cartopy_xlim
        }

    def load_base_variables(self) -> None:
        self.data.load_base_variables()

    def get_figure_size(self) -> Tuple[float, float]:
        # TODO: calculate from x, y grid count and dx, dy
        x = self.data.x_grid_count
        y = self.data.y_grid_count
        return x / 8, y / 8

    def get_time_string_by_index(self, timeidx: int = 0, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        available_times = self.data.available_times
        return available_times[timeidx][1].strftime(fmt)

    def get_slp(self, timeidx: int = 0):
        slp = self.data.sea_level_pressure(timeidx=timeidx)
        return wrf.smooth2d(slp, 50, 30)

    def get_10m_winds(self, timeidx: int = 0):
        return self.data.surface_winds(timeidx=timeidx)

    def get_contour_fill_data(self, key: str, timeidx: int) -> CTFVariable:
        ctf_var = Constants.get_contourf_variable(key)
        if key == Constants.FIELD_KEY_PREC:
            xr_variable = self.data.calculate_rain(timeidx=timeidx)

        elif key == Constants.FIELD_KEY_SNOW:
            xr_variable = self.data.calculate_snow(timeidx=timeidx)

        elif key == Constants.FIELD_KEY_WIND_10:
            xr_variable = self.data.extract_variable(var_name="uvmet10_wspd_wdir", timeidx=timeidx, units="m s-1")[0, :]
            print('here')
        else:
            xr_variable = self.data.extract_variable(var_name=key, timeidx=timeidx)

            if key == Constants.FIELD_KEY_T2:
                xr_variable = xr_variable - 273.15

        ctf_var.data_to_plot = wrf.to_np(xr_variable)
        return ctf_var

    def extract_variables(self) -> dict:
        return self.data.built_in_variables()

    def summarize_dataset(self) -> dict:
        return self.data.raw_summary

    def get_latitudes_and_longitudes(self):
        return self.data.latitudes_and_longitudes_as_np_array
