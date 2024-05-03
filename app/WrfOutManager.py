from typing import Tuple, Optional

import wrf
import math

from netCDF4 import Dataset

from app.path_config import PathConfig
from library.models.WRFData import WRFData
from library.utils import Singleton

import app.map.constants as Constants
from app.map.models import CTFVariable, CTVariable


class WrfOutManager(metaclass=Singleton):

    def __init__(self, path_config: PathConfig) -> None:
        self.path_config = path_config
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
        return 13, 13

    def get_time_string_by_index(self, timeidx: int = 0, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        available_times = self.data.available_times
        return available_times[timeidx][1].strftime(fmt)

    def get_slp(self, timeidx: int = 0):
        slp = self.data.sea_level_pressure(timeidx=timeidx)
        return wrf.smooth2d(slp, 50, 30)

    def get_10m_winds(self, timeidx: int = 0):
        return self.data.surface_winds(timeidx=timeidx)

    def get_winds(self, key: str, timeidx: int = 0):
        if key == Constants.FIELD_KEY_GEO500:
            ua, va = self.data.extract_variable("uvmet", units="km h-1", timeidx=timeidx)

            u_500 = self.data.interpolate_to_pressure_level(ua, pressure_units="hPa", level_to_interpolate=500.,
                                                            timeidx=timeidx)
            v_500 = self.data.interpolate_to_pressure_level(va, pressure_units="hPa", level_to_interpolate=500.,
                                                            timeidx=timeidx)
            return wrf.to_np(u_500), wrf.to_np(v_500)
        elif key == Constants.FIELD_KEY_WS300:
            # ua = self.data.extract_variable("ua", units="km h-1", timeidx=timeidx)
            ua, va = self.data.extract_variable("uvmet", units="km h-1", timeidx=timeidx)

            u_300 = self.data.interpolate_to_pressure_level(ua, pressure_units="hPa", level_to_interpolate=300.,
                                                            timeidx=timeidx)
            v_300 = self.data.interpolate_to_pressure_level(va, pressure_units="hPa", level_to_interpolate=300.,
                                                            timeidx=timeidx)
            return wrf.to_np(u_300), wrf.to_np(v_300)

        elif key == Constants.FIELD_KEY_TEMP850:
            ua = self.data.extract_variable("ua", units="km h-1", timeidx=timeidx)
            va = self.data.extract_variable("va", units="km h-1", timeidx=timeidx)

            u_850 = self.data.interpolate_to_pressure_level(ua, pressure_units="hPa", level_to_interpolate=850.,
                                                            timeidx=timeidx)
            v_850 = self.data.interpolate_to_pressure_level(va, pressure_units="hPa", level_to_interpolate=850.,
                                                            timeidx=timeidx)
            return wrf.to_np(u_850), wrf.to_np(v_850)

        elif key == Constants.FIELD_KEY_RH700:
            ua = self.data.extract_variable("ua", units="km h-1", timeidx=timeidx)
            va = self.data.extract_variable("va", units="km h-1", timeidx=timeidx)

            u_700 = self.data.interpolate_to_pressure_level(ua, pressure_units="hPa", level_to_interpolate=700.,
                                                            timeidx=timeidx)
            v_700 = self.data.interpolate_to_pressure_level(va, pressure_units="hPa", level_to_interpolate=700.,
                                                            timeidx=timeidx)
            return wrf.to_np(u_700), wrf.to_np(v_700)

        else:
            return self.data.surface_winds(timeidx=timeidx)

    def get_contour_data(self, key: str, timeidx: int) -> Optional[CTVariable]:
        ct_var: CTVariable = Constants.get_contour_variable(key)
        if key == Constants.FIELD_KEY_GEO500:
            # extract 500 mb heights
            height = self.data.extract_variable(var_name="z", units="dm", timeidx=timeidx)
            contour_data = self.data.interpolate_to_pressure_level(height, level_to_interpolate=500.,
                                                                   pressure_units="mb", timeidx=timeidx)

        elif key == Constants.FIELD_KEY_TEMP850:
            temp = self.data.extract_variable(var_name="tc", timeidx=timeidx)
            contour_data = self.data.interpolate_to_pressure_level(temp, level_to_interpolate=850., timeidx=timeidx)

        elif key == Constants.FIELD_KEY_RH700:
            # extract 700 mb heights
            height = self.data.extract_variable(var_name="z", units="m", timeidx=timeidx)
            contour_data = self.data.interpolate_to_pressure_level(height, level_to_interpolate=700.,
                                                                   pressure_units="hPa", timeidx=timeidx)

        elif key == Constants.FIELD_KEY_THICKNESS:
            # extract 500 mb heights
            height = self.data.extract_variable(var_name="z", units="dm", timeidx=timeidx)
            contour_data = self.data.interpolate_to_pressure_level(height, level_to_interpolate=500.,
                                                                   pressure_units="mb", timeidx=timeidx)

        elif key == Constants.FIELD_KEY_RH850:
            rh = self.data.extract_variable("rh", timeidx=timeidx)
            rh_850 = self.data.interpolate_to_pressure_level(rh, pressure_units="hPa", level_to_interpolate=850,
                                                             timeidx=timeidx)
            contour_data = rh_850.fillna(rh[0, :, :])

        else:
            contour_data = self.data.sea_level_pressure(timeidx=timeidx)

        smoothed_data = wrf.smooth2d(contour_data, 30, 20)
        ct_var.data_to_plot = smoothed_data
        return ct_var

    def get_contour_fill_data(self, key: str, timeidx: int) -> CTFVariable:
        ctf_var = Constants.get_contourf_variable(key)
        if key == Constants.FIELD_KEY_PREC:
            xr_variable = self.data.calculate_rain(timeidx=timeidx)

        elif key == Constants.FIELD_KEY_SNOW:
            xr_variable = self.data.calculate_snow(timeidx=timeidx)

        elif key == Constants.FIELD_KEY_WIND_10:
            xr_variable = self.data.extract_variable(var_name="uvmet10_wspd_wdir", timeidx=timeidx, units="m s-1")[0, :]

        elif key == Constants.FIELD_KEY_TEMP850:
            temp = self.data.extract_variable(var_name="tc", timeidx=timeidx)
            p = self.data.extract_variable(var_name="p", units="hPa", timeidx=timeidx)
            temp_850 = wrf.interplevel(temp, p, desiredlev=850.0)
            xr_variable = temp_850.fillna(temp[0, :, :])

        elif key == Constants.FIELD_KEY_THICKNESS or key == Constants.FIELD_KEY_GEO500:
            height = self.data.extract_variable("z", timeidx=timeidx, units="dm")
            terrain = self.data.extract_variable("ter", timeidx=timeidx, units="dm")

            ht_500 = self.data.interpolate_to_pressure_level(height, pressure_units="hPa", level_to_interpolate=500,
                                                             timeidx=timeidx)
            ht_1000 = self.data.interpolate_to_pressure_level(height, pressure_units="hPa", level_to_interpolate=1000,
                                                              timeidx=timeidx).fillna(0)
            virtual_temp = self.data.extract_variable("tv", timeidx=timeidx, units="K").mean(dim="bottom_top")
            Rd = 287.05  # Specific gas constant for dry air in J/kg·K
            g = 9.81  # Acceleration due to gravity in m/s^2

            delta_h = (Rd * virtual_temp / g) * math.log(1000 / 500)
            # ht_1000 = ht_1000.fillna(terrain)
            thickness_500 = ht_500 - ht_1000

            if key == Constants.FIELD_KEY_GEO500:
                # pvo_500 = self.data.interpolate_to_pressure_level(
                #     self.data.extract_variable(var_name="pvo", timeidx=timeidx),
                #     pressure_units="mb", level_to_interpolate=500.,
                #     timeidx=timeidx)
                xr_variable = self.data.interpolate_to_pressure_level(
                    self.data.extract_variable(var_name="avo", timeidx=timeidx),
                    pressure_units="mb", level_to_interpolate=500.,
                    timeidx=timeidx)
                #
                # # RVO = PVO * thickess - AVO
                #
                # # Conversion factor for absolute vorticity to SI units (1e-5/s to 1/s)
                # abs_vorticity_conversion = 1e-5
                # avo_500_si = avo_500 * abs_vorticity_conversion
                #
                # # Convert potential vorticity from PVU to SI units (10^6 m^2 s^-1 K kg^-1 to 1/s)
                # pv_conversion_factor = 1e-6
                # pvo_500_si = pvo_500 * pv_conversion_factor
                # xr_variable = pvo_500_si * thickness_500 - avo_500_si
                # xr_variable = avo_500
                # wspd = self.data.extract_variable("wspd_wdir", units="kts")[0, :]
                # xr_variable = self.data.interpolate_to_pressure_level(wspd, pressure_units="mb",
                #                                                       level_to_interpolate=500,
                #                                                       timeidx=timeidx)

            else:
                xr_variable = thickness_500

        elif key == Constants.FIELD_KEY_WS300:
            wspd, wdir = self.data.extract_variable("uvmet_wspd_wdir", units="km h-1", timeidx=timeidx)
            xr_variable = self.data.interpolate_to_pressure_level(wspd, pressure_units="hPa", level_to_interpolate=300,
                                                                  timeidx=timeidx)
        elif key == Constants.FIELD_KEY_RH700:
            rh = self.data.extract_variable("rh", timeidx=timeidx)
            rh_700 = self.data.interpolate_to_pressure_level(rh, pressure_units="hPa", level_to_interpolate=700,
                                                                  timeidx=timeidx)
            xr_variable = rh_700.fillna(rh[0, :, :])
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
