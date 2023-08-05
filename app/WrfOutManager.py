from typing import Tuple

import wrf

from netCDF4 import Dataset

from app.path_config import PathConfig
from library.models.WRFData import WRFData
from library.utils import Singleton


class WrfOutManager(metaclass=Singleton):

    def __init__(self, path_config: PathConfig) -> None:
        self.path_config = path_config
        # self.SHP_FOLDER = shape_file_folder
        self._dataset: Dataset = None
        self._data: WRFData = None

    def read_dataset(self, from_file: str) -> None:
        file_path = self.path_config.WRF_OUTPUT_FOLDER_PATH.joinpath(from_file)
        try:
            print('Creating dataset from file: ', file_path)
            self._dataset = Dataset(file_path, mode='r')
            self._data = WRFData(self._dataset)

        except Exception as e:
            print(str(e))

    def close_dataset(self) -> bool:
        success = False
        try:
            self._dataset.close()
            self._dataset = None
            success = True
            print('Closed Dataset!')
        except Exception as e:
            print(f'Exception closing netCDF4 dataset.\n{e}')
            return success

    def extract_projection_and_bounds(self) -> {}:
        return {
            "library": "cartopy",
            "projection": self._data.cartopy_proj,
            "y-limit": self._data.cartopy_ylim,
            "x-limit": self._data.cartopy_xlim
        }

    def load_base_variables(self) -> None:
        self._data.load_base_variables()

    def get_figure_size(self) -> Tuple[float, float]:
        # TODO: calculate from x, y grid count and dx, dy
        x = self._data.x_grid_count
        y = self._data.y_grid_count
        return x / 10, y / 10

    def get_available_times(self):
        return self._data.extract_all_times()

    def get_slp(self, timeidx: int = 0):
        slp = self._data.sea_level_pressure(timeidx=timeidx)
        return wrf.smooth2d(slp, 50, 30)

    def get_10m_winds(self, timeidx: int = 0):
        return self._data.surface_winds(timeidx=timeidx)

    def get_contour_fill_data(self, key: str, timeidx: int):
        # ["T2", "td2", "rh2", "mdbz", "rain", "snow"]
        if key == "snow":
            data = self._data.calculate_snow(timeidx=timeidx)
        elif key == "rain":
            data = self._data.calculate_rain(timeidx=timeidx)
        else:
            data = self._data.extract_variable(var_name=key, timeidx=timeidx)

        if key == "T2":
            # convert to celcius
            data = data - 273.15

        return wrf.to_np(data)

    def extract_variables(self) -> dict:
        return self._data.built_in_variables()

    def summarize_dataset(self) -> dict:
        return self._data.raw_summary

    def get_latitudes_and_longitudes(self):
        return self._data.latitudes_and_longitudes_as_np_array
