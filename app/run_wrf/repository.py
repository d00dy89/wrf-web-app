import os
import subprocess

from glob import glob
from pathlib import Path

from flask import current_app

from app.path_config import PathConfig

logger = current_app.logger
path_config: PathConfig = current_app.config.get("PATH_CONFIG")
WRF_INSTALL_SCRIPT = "WRF4.5_Install.bash"
WPS_FOLDER = "WPS-4.5"
WRF_FOLDER = "WRF-4.5-ARW"

WPS_FOLDER_PATH = path_config.WRF_INSTALL_FOLDER_PATH.joinpath(WPS_FOLDER)
WRF_FOLDER_PATH = path_config.WRF_INSTALL_FOLDER_PATH.joinpath(WRF_FOLDER)
WRF_RUN_FOLDER_PATH = WRF_FOLDER_PATH.joinpath("run")


def install_wrf(log_file_path: Path) -> None:
    # WRF4.5_Install.bash
    install_script_path = path_config.LIBRARY_FOLDER_PATH.joinpath(WRF_INSTALL_SCRIPT)
    # install_script_path = path_config.LIBRARY_FOLDER_PATH.joinpath("test.sh")
    log_file = open(log_file_path, "w")
    # open up a background thread to run wrf installation script.
    # TODO: do zibillion checks before opening up the installation thread
    _ = subprocess.Popen(
        ["bash", install_script_path],
        stdout=log_file,
        stderr=subprocess.STDOUT
    )


def link_ungrib_variable_table() -> str:
    logger.info("Linking Variable Table.")
    gfs_vtable = WPS_FOLDER_PATH.joinpath("ungrib/Variable_Tables/Vtable.GFS")
    wps_vtable = WPS_FOLDER_PATH.joinpath("Vtable")
    cmd_args = ["ln", "-sf", gfs_vtable.as_posix(), wps_vtable.as_posix()]
    cmd_result = subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return cmd_result.stdout.decode("utf-8")


def clean_linked_files():
    for file_name in os.listdir(WPS_FOLDER_PATH):
        if ("FILE" in file_name) or ("met_em" in file_name):
            os.remove(WPS_FOLDER_PATH.joinpath(file_name))
            logger.info(f"Removed file: {file_name}")

    for file_name in os.listdir(WRF_RUN_FOLDER_PATH):
        if "met_em" in file_name:
            os.remove(WRF_RUN_FOLDER_PATH.joinpath(file_name))
            logger.info(f"Removed file from WRF/run: {file_name}")


def clean_gfs_folder():
    old_gfs_files = [Path(wrfout) for wrfout in glob(str(path_config.GFS_FOLDER_PATH.joinpath("gfs.*")))]
    for file in old_gfs_files:
        file: Path
        os.remove(file)
        logger.info(f"Removed {file=}")


def link_grib(downloaded_gfs_files: [Path]) -> str:
    logger.info("Linking Grib data.")
    link_gfs_data_path = os.path.commonprefix(downloaded_gfs_files)
    cmd_result = subprocess.run([
        "./link_grib.csh", link_gfs_data_path,
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=WPS_FOLDER_PATH.as_posix())
    return cmd_result


def run_ungrib_exe() -> str:
    cmd_result = subprocess.run([
        "./ungrib.exe"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=WPS_FOLDER_PATH.as_posix())
    return cmd_result


def run_geogrid_exe():
    logger.info('Running geogrid.exe')
    cmd_result_geogrid_exe = subprocess.run(
        ["./geogrid.exe"], shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=WPS_FOLDER_PATH.as_posix()
    )
    cmd_stdout = cmd_result_geogrid_exe.stdout.decode("utf-8")
    result_success_message = "Successful completion of geogrid."
    if result_success_message in cmd_stdout:
        logger.info(result_success_message)
    else:
        logger.warning(f"Something wrong with geogrid.exe, details:\n{cmd_stdout}")


def run_metgrid_exe():
    logger.info('Running metgrid.exe')
    cmd_metgrid_exe = subprocess.run(
        ["./metgrid.exe"], shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=WPS_FOLDER_PATH.as_posix()
    )
    cmd_stdout = cmd_metgrid_exe.stdout.decode("utf-8")
    # out, err = cmd_metgrid_exe.communicate()
    result_success_message = "Successful completion of metgrid."
    if result_success_message in cmd_stdout:
        logger.info(result_success_message)
    else:
        logger.warning(f"Something wrong with metgrid.exe, details:\n{cmd_stdout}")


def link_metem():
    logger.info('Linking metem files.')
    cmd_link_metem = subprocess.run([
        f"ln -sf {WPS_FOLDER_PATH.joinpath('met_em.*').as_posix()} {WRF_RUN_FOLDER_PATH.as_posix()}/."
    ], shell=True)


def plot_domain():
    # run it in the output folder
    run_bp_static_folder = path_config.APP_FOLDER_PATH.joinpath("run_wrf/static")
    ncl_script_path = path_config.LIBRARY_FOLDER_PATH.joinpath("plotgrids_new_to_png.ncl")
    namelist_wps_file_path = WPS_FOLDER_PATH.joinpath("namelist.wps")

    logger.info("Plotting domain with NCL.")
    process = subprocess.Popen(["ncl", "-pQ", ncl_script_path.as_posix()],
                               cwd=run_bp_static_folder.as_posix(),
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        # TODO: maybe fix this
        #  ncl subprocess gets stuck and never returns so give it a timeout
        #  and catch the error instead of waiting forever it to return.
        outs = process.communicate(timeout=3)
    except subprocess.TimeoutExpired as error:
        logger.info(f"NCL domain output: {error}")
        process.kill()
        outs = process.communicate()

    logger.info(f"-- Ncl plot domain --\noutput:{outs}")


def run_real_exe() -> bool:
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
        logger.warning(f"Exception occurred stripping real.exe output, details:\n{e}")
    finally:
        if len(result) > 0:
            logger.warning(f"Something wrong with real.exe, details:\n{result}")
            return False
        else:
            return True


def run_wrf_exe(core_count: int) -> bool:
    # TODO: add rsl.error to logs
    logger.info(f"Running wrf.exe with core count: {core_count}")
    # TODO: --use-hwthread-cpus for maxing out process count
    run_wrf_process = subprocess.Popen(
        ["mpirun", "-np", str(core_count), "./wrf.exe"],
        cwd=WRF_RUN_FOLDER_PATH.as_posix(),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    run_success = False
    # TODO: make communicate optional for user
    try:
        out = run_wrf_process.communicate()
        logger.info(f"wrf.exe completed with output: {out}")
        run_success = True
    except Exception as e:
        logger.warning(f"Exception occurred details:\n{e}")

    finally:
        return run_success


def move_wrf_outs():
    wrf_out_paths = [Path(wrfout) for wrfout in glob(str(WRF_RUN_FOLDER_PATH.joinpath("wrfout_*")))]
    new_wrf_out_paths = [path_config.WRF_OUTPUT_FOLDER_PATH.joinpath(path.name) for path in wrf_out_paths]
    # TODO: check params
    try:
        for src, target in zip(wrf_out_paths, new_wrf_out_paths):
            src.rename(target)
            logger.info(f"Moved from: {src=} To {target=}")
        # logger.info("Moved wrfout files to app data directory.")
    except Exception as e:
        logger.warning(f'Exception occurred while moving wrfout files, details: \n{e}')
