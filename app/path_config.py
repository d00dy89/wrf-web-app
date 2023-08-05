import logging

from pathlib import Path


class PathConfig:

    PROJECT_PATH = Path(__file__).parent.parent  # /path/to/wrf-web-app
    # FLASK APP
    APP_FOLDER_PATH = PROJECT_PATH.joinpath("app")  # ../wrf-web-app/app
    LIBRARY_FOLDER_PATH = PROJECT_PATH.joinpath("library")
    LOGS_FOLDER = PROJECT_PATH.joinpath("logs")
    # RESOURCES_FOLDER_PATH = PROJECT_PATH.joinpath("resources")

    # WRF RUN RELATED
    WRF_INSTALL_FOLDER_PATH = PROJECT_PATH.joinpath("Build_WRF")  # ../wrf-web-app/Build_WRF
    WRF_INTERNAL_DATA_PATH = WRF_INSTALL_FOLDER_PATH.joinpath("DATA")  # ../wrf-web-app/Build_WRF/DATA

    # WRF OUTPUT
    WRF_OUTPUT_FOLDER_PATH = WRF_INTERNAL_DATA_PATH.joinpath("WRFOUT")

    # EXTERNAL DOWNLOAD
    GFS_FOLDER_PATH = WRF_INTERNAL_DATA_PATH.joinpath("GFS")  # /Build_WRF/DATA/GFS
    GFS_BACKUP_FOLDER = WRF_INTERNAL_DATA_PATH.joinpath("GFS_BACKUP")  # # /Build_WRF/DATA/GFS_BACKUP

    def create_folders(self, logger: logging.Logger) -> None:
        for key in dir(self):
            if key.startswith('__') or key.islower():
                pass
            else:
                path = self.__getattribute__(key)
                if not path.exists():
                    path.mkdir(parents=True)
                    logger.info(f'Created {path=}.')
