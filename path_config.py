from pathlib import Path


class PathConfig:

    PROJECT_PATH = Path(__file__).parent  # /path/to/wrf-web-app
    # FLASK APP
    APP_FOLDER_PATH = PROJECT_PATH.joinpath("app")  # ../wrf-web-app/app
    DATA_FOLDER_PATH = PROJECT_PATH.joinpath("data")  # ../wrf-web-app/data
    LIBRARY_FOLDER_PATH = PROJECT_PATH.joinpath("library")
    LOGS_FOLDER = PROJECT_PATH.joinpath("logs")
    # RESOURCES_FOLDER_PATH = PROJECT_PATH.joinpath("resources")
    # WRF RUN RELATED
    WRF_INSTALL_FOLDER_PATH = PROJECT_PATH.joinpath("Build_WRF")
    WRF_INTERNAL_DATA_PATH = WRF_INSTALL_FOLDER_PATH.joinpath("DATA")
    GFS_FOLDER_PATH = WRF_INTERNAL_DATA_PATH.joinpath("GFS")  # ../data/gfs

    # WRF OUTPUT RELATED
    WRF_OUTPUT_FOLDER_PATH = DATA_FOLDER_PATH.joinpath("wrf")  # ../data/wrf

    def __init__(self) -> None:
        for key in dir(self):
            if not key.startswith('__'):
                path = self.__getattribute__(key)
                if not path.exists():
                    path.mkdir()
                    print(f'Created {path=}.')
