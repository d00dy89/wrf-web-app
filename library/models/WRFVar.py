import wrf
import xarray
import numpy as np

from netCDF4 import Dataset


class WRFVar:

    _data: xarray.Variable

    def __init__(self, wrf_dataset: Dataset, var_key: str, **get_var_kwargs) -> None:
        self.key = var_key
        self._data = wrf.getvar(wrf_dataset, var_key)

    @property
    def data(self) -> xarray.DataArray:
        return self._data

    def as_np_array(self) -> np.ndarray:
        return wrf.to_np(self._data)

