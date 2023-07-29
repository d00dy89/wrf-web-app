import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
import pandas as pd

from path_config import PathConfig

# TODO:
# def calculate_earliest_possible_gfs_date():
#     utc_now = datetime.utcnow()
# earliest_possible_gfs_date = calculate_earliest_possible_gfs_date()


class GfsDownloader:
    _resolution = "1p00"
    # https://www.ftp.ncep.noaa.gov/data/nccf/com/gfs/prod/gfs.20230717/12/atmos/gfs.t12z.pgrb2.1p00.f000
    _base_url = "https://www.ftp.ncep.noaa.gov/data/nccf/com/gfs/prod"  # + gfs.20230717/12/atmos/gfs.t12z.pgrb2.1p00.f000

    def __init__(self, path_config: PathConfig):
        self.path_config = path_config

    def download(self, start_date: datetime, end_date: datetime, interval_hours: int) -> [Path]:
        dates_to_fetch = pd.date_range(start_date, end_date, freq=f"{interval_hours}H", inclusive="both")
        file_paths = []
        for date in dates_to_fetch:
            self._make_date_directory_tree(date)
            date_folder = date.strftime("%Y%m%d")
            url = self.generate_gfs_url(date)
            gfs_file_name = url.split("/")[-1]
            file_path = self._download_and_write_to_file(url=url, date_folder=date_folder, file_name_to_save=gfs_file_name)
            os.symlink(file_path, self.path_config.GFS_FOLDER_PATH.joinpath(file_path.name))
            file_paths.append(file_path)

        return file_paths

    def generate_gfs_url(self, date: datetime) -> str:
        date_str = date.strftime('%Y%m%d')
        base_run_hour_str = self.get_base_run_hour(for_date=date)
        distance_in_hour_str = self.distance_in_hour_string_of_gfs(for_date=date)

        # fetch for 3 hour input interval
        # gfs.20230717/00/atmos/gfs.t00z.pgrb2.1p00.f000
        # gfs.20230717/00/atmos/gfs.t00z.pgrb2.1p00.f003
        # gfs.20230717/06/atmos/gfs.t06z.pgrb2.1p00.f000
        # gfs.20230717/12/atmos/gfs.t12z.pgrb2.1p00.f003
        gfs_file_name = f"gfs.t{base_run_hour_str}z.pgrb2.{self._resolution}.f{distance_in_hour_str.zfill(3)}"
        return f"{self._base_url}/gfs.{date_str}/{base_run_hour_str}/atmos/{gfs_file_name}"

    def _make_date_directory_tree(self, date: datetime) -> None:
        date_folder_path = self.path_config.GFS_FOLDER_PATH.joinpath(date.strftime("%Y%m%d"))
        if date_folder_path.exists():
            return

        try:
            os.makedirs(date_folder_path)
        except OSError as file_exists_error:
            print(f"Could not create directory tree for {date_folder_path}, details: \n{file_exists_error}")

    def _download_and_write_to_file(self, url: str, date_folder: str, file_name_to_save: str) -> Path:
        file_path = self.path_config.GFS_FOLDER_PATH.joinpath(f'{date_folder}/{file_name_to_save}')
        if file_path.exists():
            return file_path  # early exit if file exists

        try:
            print(f"Starting to download to {date_folder}/{file_name_to_save}.")
            response = requests.get(url)
            with open(file_path, "wb") as gfs_file:
                gfs_file.write(response.content)
            print(f"Downloaded and saved file to {file_path=}")
        except Exception as e:
            print(f"Excetion occurred downloading {file_name_to_save} details:{e}")
        finally:
            return file_path

    @staticmethod
    def distance_in_hour_string_of_gfs(for_date: datetime) -> str:
        hour_remainder = for_date.hour % 6
        if hour_remainder >= 0:
            hour_str = str(hour_remainder)
        else:
            hour_str = for_date.strftime("%H")

        return hour_str

    @staticmethod
    def get_base_run_hour(for_date: datetime) -> str:
        hour = for_date.hour
        if 0 <= hour < 6:
            base_run_hour = 0
        elif 6 <= hour < 12:
            base_run_hour = 6
        elif 12 <= hour < 18:
            base_run_hour = 12
        else:
            base_run_hour = 18
        return str(base_run_hour).zfill(2)
