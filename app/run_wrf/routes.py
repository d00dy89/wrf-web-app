import os

from pathlib import Path
from time import sleep
from datetime import datetime, timedelta

from flask import request, render_template, url_for, redirect, session, current_app, flash

import app.run_wrf.repository as run_repository

from app.run_wrf import run_wrf_bp
from app.run_wrf.forms import WpsForm, DomainForm, WrfForm
from app.path_config import PathConfig
from library.GfsDownloader import GfsDownloader

logger = current_app.logger
path_config: PathConfig = current_app.config.get("PATH_CONFIG")
gfs_downloader = GfsDownloader(path_config)
WRF_INSTALL_SCRIPT = "WRF4.5_Install.bash"
WPS_FOLDER = "WPS-4.5"
WRF_FOLDER = "WRF-4.5-ARW"

WPS_FOLDER_PATH = path_config.WRF_INSTALL_FOLDER_PATH.joinpath(WPS_FOLDER)
WRF_FOLDER_PATH = path_config.WRF_INSTALL_FOLDER_PATH.joinpath(WRF_FOLDER)
geog_data_path = path_config.WRF_INSTALL_FOLDER_PATH.joinpath("WPS_GEOG")

WRF_RUN_FOLDER_PATH = WRF_FOLDER_PATH.joinpath("run")
wps_namelist_path = WPS_FOLDER_PATH.joinpath("namelist.wps")
max_dom = 1
log_time_fmt = '%H-%M-%S_%d-%m-%Y'
gfs_start_arg = "gfs_start_datetime"
gfs_end_arg = "gfs_end_datetime"
model_input_arg = "model_input_in_seconds"
model_out_arg = "model_output_in_minutes"
frame_count_arg = "frame"


@run_wrf_bp.route('/', methods=["GET", "POST"])
def index():
    # check if WRF is installed if not give an option to install it
    build_wrf_folder_contents = os.listdir(path_config.WRF_INSTALL_FOLDER_PATH)
    # TODO: add a better check here
    is_wrf_installed = any("WRF" in file for file in build_wrf_folder_contents)
    if is_wrf_installed:
        return redirect(url_for(".run_wrf"))
    else:
        return render_template("run_wrf/index.html")


@run_wrf_bp.route("/install", methods=["GET"])
def install():
    # return log filename to user
    install_log_file = f"wrf_installation_{datetime.utcnow().strftime(log_time_fmt)}.log"
    log_file_path = path_config.LOGS_FOLDER.joinpath(install_log_file)
    run_repository.install_wrf(log_file_path)
    return render_template("run_wrf/installation.html", installation_log_file=install_log_file)


@run_wrf_bp.route("/configure", methods=["GET", "POST"])
def run_wrf():
    form = WpsForm()
    if request.method != "POST":
        return render_template("run_wrf/run.html", form=form)
    else:
        if not form.validate_on_submit():
            # return with errors
            return render_template("run_wrf/run.html", form=form)

        # GFS DATA INPUT PARAMETERS
        gfs_start_date = form.start_date.data
        gfs_end_date = form.end_date.data
        gfs_start_hour = form.start_hour.data
        gfs_end_hour = form.end_hour.data
        # TODO: maybe handle date and time separate
        gfs_start_datetime = datetime.combine(gfs_start_date, datetime.strptime(gfs_start_hour, "%H").time())
        gfs_end_datetime = datetime.combine(gfs_end_date, datetime.strptime(gfs_end_hour, "%H").time())
        time_diff = gfs_end_datetime - gfs_start_datetime
        model_input_in_hours = form.model_input_interval_in_hours.data  # input interval

        # why is this tuple
        # TODO: separate model input and output form
        model_input_in_seconds = model_input_in_hours * 60 * 60,
        interval_seconds = model_input_in_seconds[0]
        session[model_input_arg] = interval_seconds
        session[gfs_start_arg] = gfs_start_datetime
        session[gfs_end_arg] = gfs_end_datetime

        model_output_in_minutes = form.model_output_interval_in_minutes.data  # output interval
        session[model_out_arg] = model_output_in_minutes
        session[frame_count_arg] = int(time_diff.total_seconds() / (model_output_in_minutes * 60)) + 1

        run_repository.clean_gfs_folder()

        # end_date must be at least 6 hours earlier
        downloaded_files: [Path] = gfs_downloader.download(
            start_date=gfs_start_datetime,
            end_date=gfs_end_datetime,
            interval_hours=model_input_in_hours
        )
        session["downloaded_files"] = downloaded_files
        # update Vtable
        run_repository.link_ungrib_variable_table()

        # removes FILE, GRIBFILE and met_em files
        run_repository.clean_linked_files()
        sleep(1)

        return redirect(url_for('run_wrf_bp.wps'))


@run_wrf_bp.route('/wps', methods=["GET", "POST"])
def wps():
    form = DomainForm()
    if not request.method == "POST":
        return render_template("run_wrf/wps.html", form=form)
    else:
        if not form.validate_on_submit():
            return render_template("run_wrf/wps.html", form=form)

        e_we = form.east_west_grid_count.data
        e_sn = form.north_south_grid_count.data
        dxdy = form.grid_resolution.data
        dx_dy = f"{dxdy}000"
        session["e_we"] = e_we
        session["e_sn"] = e_sn
        session["dx_dy"] = dx_dy

        ref_lat = form.ref_lat.data  # center lat
        ref_lon = form.ref_lon.data  # center lon
        truelat1 = form.true_lat_1.data  # lambert true lat 1
        truelat2 = form.true_lat_2.data  # lambert true lat 2
        # TODO: include standard lon to center lat lon validation
        stand_lon = ref_lat
        try:
            # model_input_in_hours * 60 * 60
            interval_seconds = session.get(model_input_arg, "input-interval-not-set")
            gfs_start_date = session.get(gfs_start_arg, "gfs-start-not-set").strftime("%Y-%m-%d_%H:%M:%S")
            gfs_end_date = session.get(gfs_end_arg, "gfs-end-not-set").strftime("%Y-%m-%d_%H:%M:%S")
        except Exception as e:
            print(f"GFS config not found details: {e}")
            return redirect(url_for(".run_wrf"))

        namelist_wps_content = render_template(
            "namelists/namelist.wps",
            max_dom=max_dom,
            gfs_start_date=gfs_start_date,
            gfs_end_date=gfs_end_date,
            interval_seconds=interval_seconds,
            geog_data_path=geog_data_path,
            e_we=e_we,
            e_sn=e_sn,
            dx=dx_dy,
            dy=dx_dy,
            ref_lat=ref_lat,
            ref_lon=ref_lon,
            truelat1=truelat1,
            truelat2=truelat2,
            stand_lon=ref_lon  # TODO: include standard lon
        )

        with open(wps_namelist_path, 'w') as wps_file:
            wps_file.write(namelist_wps_content)

        sleep(.2)
        # link grib
        downloaded_files = session.pop("downloaded_files")
        run_repository.link_grib(downloaded_files)
        run_repository.run_ungrib_exe()

        return redirect(url_for('.domain'))


@run_wrf_bp.route('/domain', methods=["GET", "POST"])
def domain():
    if request.method == "POST":
        sleep(.1)
        run_repository.run_geogrid_exe()
        sleep(.1)
        run_repository.run_metgrid_exe()
        sleep(.1)
        run_repository.link_metem()
        return redirect(url_for('run_wrf_bp.wrf'))
    else:
        run_repository.plot_domain()
        return render_template("run_wrf/domain.html")


@run_wrf_bp.route('/wrf', methods=["GET", "POST"])
def wrf():
    form = WrfForm()
    if request.method != "POST":
        return render_template("run_wrf/wrf.html", form=form)
    else:

        if not form.validate_on_submit():
            return render_template("run_wrf/wrf.html", form=form)

        microphy = form.microphy.data
        pbl = form.pbl.data
        cumulus = form.cumulus.data
        core = form.core.data

        start_date: datetime = session.get(gfs_start_arg, "not-set")
        end_date: datetime = session.get(gfs_end_arg, "not-set")

        session.get(gfs_start_arg, "not-set")
        session.get(gfs_start_arg, "not-set")
        session.get(gfs_start_arg, "not-set")

        start_year = start_date.strftime("%Y")
        start_month = start_date.strftime("%m")
        start_day = start_date.strftime("%d")
        start_hour = start_date.strftime("%H")

        end_year = end_date.strftime("%Y")
        end_month = end_date.strftime("%m")
        end_day = end_date.strftime("%d")
        end_hour = end_date.strftime("%H")

        interval_seconds = session.get(model_input_arg, "not-set")
        history_interval = session.get(model_out_arg, "not-set")

        e_we = session.get("e_we", "not-set")
        e_sn = session.get("e_sn", "not-set")
        dx_dy = session.get("dx_dy", "not-set")
        frame_per_outfile = session.get(frame_count_arg, "not-set")

        run_time_period: timedelta = end_date - start_date
        run_days = run_time_period.days
        seconds_in_hour = 60 * 60
        run_hours = int(run_time_period.seconds / seconds_in_hour)

        namelist_input_path = WRF_RUN_FOLDER_PATH.joinpath("namelist.input")
        namelist_input_content = render_template(
            "namelists/namelist.input",
            max_dom=max_dom,
            run_days=str(run_days),
            run_hours=str(run_hours),
            run_minutes="00",
            run_seconds="00",
            start_year=start_year,
            start_month=start_month,
            start_day=start_day,
            start_hour=start_hour,
            end_year=end_year,
            end_month=end_month,
            end_day=end_day,
            end_hour=end_hour,
            interval_seconds=interval_seconds,
            history_interval=history_interval,
            frame_per_outfile=frame_per_outfile,
            e_we=e_we,
            e_sn=e_sn,
            dx=dx_dy,
            dy=dx_dy,
            time_step=int(dx_dy) * 6,  # must be higher than 6x dx or dy
            microphy=microphy,
            cumulus=cumulus,
            pbl=pbl
        )
        with open(namelist_input_path, 'w') as wps_file:
            wps_file.write(namelist_input_content)

        sleep(2)
        is_run_ok = run_repository.run_real_exe()
        if not is_run_ok:
            flash("Please check your WRF configuration.")
            return redirect(url_for(".wrf"))

        logger.info(f"Successful real.exe run, continuing with wrf.exe with core count: {core}")
        run_success = run_repository.run_wrf_exe(core_count=core)
        if run_success:
            run_repository.move_wrf_outs()
            return redirect(url_for("file_selection_bp.index"))
        else:
            return redirect(url_for("run_wrf_bp.run"))
