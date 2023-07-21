import os
import subprocess

import requests
from pathlib import Path
from flask import current_app

from path_config import PathConfig

path_config: PathConfig = current_app.config.get("PATH_CONFIG")
WRF_INSTALL_SCRIPT = "WRF4.5_Install.bash"
WPS_FOLDER = "WPS-4.5"
WRF_FOLDER = "WRF-4.5-ARW"

WPS_FOLDER_PATH = path_config.WRF_INSTALL_FOLDER_PATH.joinpath(WPS_FOLDER)
WRF_FOLDER_PATH = path_config.WRF_INSTALL_FOLDER_PATH.joinpath(WRF_FOLDER)
WRF_RUN_FOLDER_PATH = WRF_FOLDER_PATH.joinpath("run")


def download_gfs_and_write_to_file(url: str, file_name_to_save: str) -> None:
    file_path = path_config.GFS_FOLDER_PATH.joinpath(file_name_to_save)
    if file_path.exists():
        return

    try:
        print("Starting to download.")
        response = requests.get(url)
        with open(file_path, "wb") as gfs_file:
            gfs_file.write(response.content)
        print(f"Downloaded and saved file to {file_path=}")
    except Exception as e:
        print(f"Excetion occurred downloading {file_name_to_save} details:{e}")


def install_wrf(log_file_path: Path) -> None:
    # WRF4.5_Install.bash
    # install_script_path = path_config.library_folder.joinpath(WRF_INSTALL_SCRIPT)
    install_script_path = path_config.LIBRARY_FOLDER_PATH.joinpath("test.sh")
    log_file = open(log_file_path, "w")
    # open up a background thread to run wrf installation script.
    # TODO: do zibillion checks before opening up the installation thread
    _ = subprocess.Popen(
        ["bash", install_script_path],
        stdout=log_file,
        stderr=subprocess.STDOUT
    )


def link_ungrib_variable_table() -> str:
    print("Linking Variable Table.")
    gfs_vtable = WPS_FOLDER_PATH.joinpath("ungrib/Variable_Tables/Vtable.GFS")
    wps_vtable = WPS_FOLDER_PATH.joinpath("Vtable")
    cmd_args = ["ln", "-sf", gfs_vtable.as_posix(), wps_vtable.as_posix()]
    cmd_result = subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return cmd_result.stdout.decode("utf-8")


def link_grib() -> str:
    print("Linking Grib data.")
    # TODO: unify model file names with download method
    link_gfs_data_path = path_config.GFS_FOLDER_PATH.joinpath("gfs")
    cmd_result = subprocess.run([
        "./link_grib.csh", link_gfs_data_path.as_posix(),
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=WPS_FOLDER_PATH.as_posix())
    return cmd_result


def run_ungrib_exe() -> str:
    cmd_result = subprocess.run([
        "./ungrib.exe"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=WPS_FOLDER_PATH.as_posix())
    return cmd_result


def run_geogrid_exe():
    print('Running geogrid.exe')
    cmd_result_geogrid_exe = subprocess.run(
        ["./geogrid.exe"], shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=WPS_FOLDER_PATH.as_posix()
    )
    cmd_stdout = cmd_result_geogrid_exe.stdout.decode("utf-8")
    result_success_message = "Successful completion of geogrid."
    if result_success_message in cmd_stdout:
        print(result_success_message)
    else:
        print(f"Something wrong with geogrid.exe, details:\n{cmd_stdout}")


def run_metgrid_exe():
    metgrid_exe_file_path = WPS_FOLDER_PATH.joinpath("metgrid.exe")
    print('Running metgrid.exe')
    cmd_metgrid_exe = subprocess.run(
        ["./metgrid.exe"], shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=WPS_FOLDER_PATH.as_posix()
    )
    cmd_stdout = cmd_metgrid_exe.stdout.decode("utf-8")
    # out, err = cmd_metgrid_exe.communicate()
    result_success_message = "Successful completion of metgrid."
    if result_success_message in cmd_stdout:
        print(result_success_message)
    else:
        print(f"Something wrong with metgrid.exe, details:\n{cmd_stdout}")


def link_metem():
    print('Linking metem files.')
    cmd_link_metem = subprocess.run([
        f"ln -sf {WPS_FOLDER_PATH.joinpath('met_em.*').as_posix()} {WRF_RUN_FOLDER_PATH.as_posix()}/."
    ], shell=True)


def plot_domain():
    # run it in the output folder
    run_bp_static_folder = path_config.APP_FOLDER_PATH.joinpath("run_wrf/static")
    ncl_script_path = path_config.LIBRARY_FOLDER_PATH.joinpath("plotgrids_new_to_png.ncl")
    namelist_wps_file_path = WPS_FOLDER_PATH.joinpath("namelist.wps")
    fname_arg = "'wpsFilePath=\"{}\"'".format(namelist_wps_file_path.as_posix())
    cmd = f"ncl -pQ {fname_arg} {ncl_script_path.as_posix()}"
    try:
        # TODO: maybe fix this
        #  ncl subprocess gets stuck and never returns to give it a timeout
        #  and catch the error instead of waiting forever it to return.
        result = subprocess.run([cmd], shell=True, cwd=run_bp_static_folder.as_posix(), timeout=3,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.TimeoutExpired as error:
        pass

    print("Plotted domain grids.")


def run_real_exe():
    em_real_exe_file_path = WRF_FOLDER_PATH.joinpath('test/em_real/real.exe')
    cmd_real_run = subprocess.run(
        ["./real.exe"],
        cwd=WRF_RUN_FOLDER_PATH.as_posix(), shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    real_exe_success_output = 'starting wrf task            0  of            1\n'
    result = cmd_real_run.stdout.decode("utf-8")
    result_success_message = "Successful completion of real.exe."
    try:
        result = result.strip(real_exe_success_output)
    except Exception as e:
        print(f"Exception occurred stripping real.exe output, details:\n{e}")

    finally:
        if len(result) > 0:
            print(f"Something wrong with real.exe, details:\n{result}")
        else:
            print(result_success_message)


def run_wrf_exe(log_file_name: str):
    wrf_run_log_file_path = path_config.LOGS_FOLDER.joinpath(log_file_name)
    log_file = open(wrf_run_log_file_path, "w")
    cmd_run_wrf = subprocess.Popen(
        ["mpirun", "-np", "2", "./wrf.exe"],
        cwd=WRF_RUN_FOLDER_PATH.as_posix(),
        stdout=log_file, stderr=subprocess.STDOUT
    )
    return cmd_run_wrf
