from datetime import datetime
from typing import Tuple

import wrf
import pandas as pd
import numpy as np
import xarray as xr

from netCDF4 import Dataset


class WRFData:
    _pres_variable_name = 'p'
    _height_variable_name = 'z'
    _terrain_variable_name = "ter"

    def __init__(self, ds: Dataset) -> None:
        self.ds = ds
        self.title = self.ds.TITLE
        self.map_proj = self.ds.MAP_PROJ_CHAR
        self.cen_lat = self.ds.CEN_LAT
        self.cen_lon = self.ds.CEN_LON
        self.dx = self.ds.DX
        self.dy = self.ds.DY
        self.dt = self.ds.DT
        self.model_type = self.ds.SIMULATION_INITIALIZATION_TYPE
        self.simulation_start_date = self.ds.SIMULATION_START_DATE

        self._available_times: [dict] = []
        self._terrain_var: xr.DataArray = None
        self._pressure_levels_hpa: xr.DataArray = None
        self._height_in_meters: xr.DataArray = None
        self._slp_var: xr.DataArray = None
        self._base_vars_loaded: bool = False

    def __repr__(self) -> str:
        return f"Run{self.title} {self.model_type} simulation start {self.simulation_start_date}."

    @property
    def raw_summary(self) -> dict:
        return {
            "projection": self.map_proj,
            "centralLatitude": self.cen_lat,
            "centralLongitude": self.cen_lon,
            "dX": self.dx,
            "dY": self.dy,
            "dT": self.dt,
            "startDate": self.simulation_start_date,
            "numTimeSteps": len(self.ds.dimensions['Time'])
        }

    def sea_level_pressure(self, timeidx: int = 0, unit: str = "hPa"):
        return self.extract_variable("slp", timeidx=timeidx, units=unit)

    def surface_winds(self, timeidx: int = 0, unit: str = "m s-1"):
        return self.extract_variable("uvmet10", timeidx=timeidx, units=unit, meta=False)

    def load_base_variables(self):
        # TODO: consider cache
        self._terrain_var = self.extract_variable(
            var_name=self._terrain_variable_name,
            timeidx=0
        )
        # self._slp_var = self.extract_variable(
        #     var_name="slp",
        #     timeidx=0
        # )
        # self._pressure_levels_hpa = self.extract_variable(
        #     var_name=self._pres_variable_name,
        #     timeidx=0,
        #     units='hPa')
        # self._height_in_meters = self.extract_variable(
        #     var_name=self._height_variable_name,
        #     timeidx=0,
        #     units='m')
        self._base_vars_loaded = True

    def extract_all_times(self) -> [dict]:
        all_times = wrf.extract_times(wrfin=self.ds, timeidx=wrf.ALL_TIMES)
        return [{
            'idx': idx,
            'date': datetime.fromisoformat(pd.to_datetime(date).isoformat())
        } for idx, date in enumerate(all_times)]

    def built_in_variables(self) -> dict:
        _variables = {}
        for var_name, nc_var in self.ds.variables.items():
            _variables[var_name] = {
                "dimensions": nc_var.dimensions,
                "shape": nc_var.shape
            }
        return _variables

    def extract_variables(self) -> dict:
        return self.built_in_variables()

    @property
    def available_times(self) -> dict:
        self._available_times = self.extract_all_times()
        return self._available_times

    @property
    def latitudes_and_longitudes_as_np_array(self) -> Tuple[np.ndarray, np.ndarray]:
        return wrf.latlon_coords(self._terrain_var, as_np=True)

    @property
    def cartopy_proj(self):
        return wrf.get_cartopy(wrfin=self.ds)

    @property
    def cartopy_xlim(self):
        return wrf.cartopy_xlim(wrfin=self.ds)

    @property
    def cartopy_ylim(self):
        return wrf.cartopy_ylim(wrfin=self.ds)

    def extract_variable(self, var_name: str, *args, **kwargs) -> xr.DataArray:
        # TODO: consider cache
        return wrf.getvar(wrfin=self.ds, varname=var_name, *args, **kwargs)

    def extract_variable_to_np(self, *args, **kwargs) -> np.ndarray:
        return wrf.to_np(self.extract_variable(*args, **kwargs))

    def extract_projection_params(self):
        return wrf.get_proj_params(wrfin=self.ds)

    def extract_variables(self, variables_list: [str], time_index: int) -> dict:
        result = {
            'meta': 'xarray meta data',
            'selected_time': '',
            'variables': []
        }

        for varname in variables_list:
            result['variables'].append(wrf.getvar(wrfin=self.ds, varname=varname, timeidx=time_index))

    def calculate_snow(self, timeidx: int = 0):
        """
        "SNOW" "SNOWH" "SNOWNC"

        :return:
        """
        t_now = self.extract_variable(var_name="SNOW", timeidx=timeidx, meta=False)
        t_past = self.extract_variable(var_name="SNOW", timeidx=timeidx-1, meta=False)
        return t_now - t_past

    def calculate_rain(self, timeidx: int = 0):
        """
        "RAINSH" "RAINC" "RAINNC"
        :return:
        """
        rain_sum_now = self.extract_variable("RAINC", timeidx=timeidx, meta=False) + self.extract_variable("RAINC", timeidx=timeidx, meta=False)
        rain_sum_past = self.extract_variable("RAINC", timeidx=timeidx-1, meta=False) + self.extract_variable("RAINC", timeidx=timeidx-1, meta=False)
        return rain_sum_now - rain_sum_past
