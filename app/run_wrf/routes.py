import os

from time import sleep
from datetime import date, datetime

import app.run_wrf.repository as run_repository
from flask import request, render_template, url_for, redirect, send_file, current_app, flash

from app.run_wrf import run_wrf_bp
from path_config import PathConfig

path_config: PathConfig = current_app.config.get("PATH_CONFIG")
WRF_INSTALL_SCRIPT = "WRF4.5_Install.bash"
WPS_FOLDER = "WPS-4.5"
WRF_FOLDER = "WRF-4.5-ARW"

WPS_FOLDER_PATH = path_config.WRF_INSTALL_FOLDER_PATH.joinpath(WPS_FOLDER)
WRF_FOLDER_PATH = path_config.WRF_INSTALL_FOLDER_PATH.joinpath(WRF_FOLDER)
WRF_RUN_FOLDER_PATH = WRF_FOLDER_PATH.joinpath("run")

max_dom = 1
log_time_fmt = '%H-%M-%S_%d-%m-%Y'


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


def download_gfs():
    d0 = date(int(sd.split('-')[0]), int(sd.split('-')[1]), int(sd.split('-')[2]))
    d1 = date(int(ed.split('-')[0]), int(ed.split('-')[1]), int(ed.split('-')[2]))
    fark_saat = (int(gfs_bitis_saati) - int(gfs_baslangic_saati))
    farkdate = d1 - d0
    hour = (farkdate.days) * 24 + int(fark_saat)

    adimsayisi = int(isec)

    # download gfs
    for i in range(0, int(hour) + int(adimsayisi), int(adimsayisi)):
        forecastHour = ""
        if int(i / 100) != 0:
            forecastHour = "f" + str(i)
        elif int(i / 10) != 0:
            forecastHour = "f0" + str(i)
        else:
            forecastHour = "f00" + str(i)

        gfs_file_name = f"gfs.t{gfs_baslangic_saati}z.pgrb2.1p00.{forecastHour}"
        url = f'https://www.ftp.ncep.noaa.gov/data/nccf/com/gfs/prod/gfs.{sd.replace("-", "")}/{gfs_baslangic_saati}/atmos/{gfs_file_name}'

        run_repository.download_gfs_and_write_to_file(url, file_name_to_save=gfs_file_name)


@run_wrf_bp.route("/configure", methods=["GET", "POST"])
def run_wrf():
    if request.method != "POST":
        return render_template("run_wrf/run.html")
    else:
        # TODO: store globals on session or on flask <g> object or use in query
        global sd
        global ed
        global isec
        global gfs_baslangic_saati
        global gfs_bitis_saati
        global fark_saat
        global farkdate

        sd = request.form.get("start_date")  # string şeklinde yyyy-aa-gg formatında
        ed = request.form.get("end_date")
        isec = request.form.get("interval_seconds")
        gfs_baslangic_saati = request.form.get("gfsBaslangicSaati")
        gfs_bitis_saati = request.form.get("gfsBitisSaati")
        d0 = date(int(sd.split('-')[0]), int(sd.split('-')[1]), int(sd.split('-')[2]))
        d1 = date(int(ed.split('-')[0]), int(ed.split('-')[1]), int(ed.split('-')[2]))
        fark_saat = (int(gfs_bitis_saati) - int(gfs_baslangic_saati))
        farkdate = d1 - d0
        hour = (farkdate.days) * 24 + int(fark_saat)

        adimsayisi = int(isec)

        # START RUNNING
        # what is this ? Shows GFS variables vs VTABLE
        # familiar = 'cd /home/miade/Build_WRF/WPS-4.3/util/ && ./g2print.exe ' \
        #            '/home/miade/Build_WRF/DATA/gfs* >& g2print.log'
        # os.system(familiar)

        download_gfs()
        # update Vtable
        run_repository.link_ungrib_variable_table()

        # link grib
        run_repository.link_grib()

        run_repository.run_ungrib_exe()
        return redirect(url_for('run_wrf_bp.wps'))


@run_wrf_bp.route('/wps', methods=["GET", "POST"])
def wps():
    if not request.method == "POST":
        return render_template("run_wrf/wps.html")
    else:
        global e_we
        global e_sn
        global dxdy
        global ref_lat
        global ref_lon
        global truelat1
        global truelat2
        global stand_lon

        e_we = request.form.get("e_we")
        e_sn = request.form.get("e_sn")
        dxdy = request.form.get("dxdy")
        ref_lat = request.form.get("ref_lat")
        ref_lon = request.form.get("ref_lon")
        truelat1 = request.form.get("truelat1")
        truelat2 = request.form.get("truelat2")
        stand_lon = request.form.get("stand_lon")

        gfs_start_date = sd + "_" + gfs_baslangic_saati + ":00:00"
        gfs_end_date = ed + "_" + gfs_bitis_saati + ":00:00"
        interval_seconds = str(int(isec) * 3600)

        geog_data_path = path_config.WRF_INSTALL_FOLDER_PATH.joinpath("WPS_GEOG")
        wps_namelist_path = WPS_FOLDER_PATH.joinpath("namelist.wps")

        namelist_wps_content = render_template(
            "namelists/namelist.wps",
            max_dom=max_dom,
            gfs_start_date=gfs_start_date,
            gfs_end_date=gfs_end_date,
            interval_seconds=interval_seconds,
            geog_data_path=geog_data_path,
            e_we=e_we,
            e_sn=e_sn,
            dx=dxdy + "000",
            dy=dxdy + "000",
            ref_lat=ref_lat,
            ref_lon=ref_lon,
            truelat1=truelat1,
            truelat2=truelat2,
            stand_lon=ref_lon
        )

        with open(wps_namelist_path, 'w') as wps_file:
            wps_file.write(namelist_wps_content)

        sleep(.2)
        return redirect(url_for('.domain'))


@run_wrf_bp.route('/domain', methods=["GET", "POST"])
def domain():
    if request.method == "POST":
        run_repository.run_geogrid_exe()
        run_repository.run_metgrid_exe()
        run_repository.link_metem()
        return redirect(url_for('run_wrf_bp.wrf'))
    else:
        run_repository.plot_domain()
        return render_template("run_wrf/domain.html")


@run_wrf_bp.route('/wrf', methods=["GET", "POST"])
def wrf():
    if request.method == "POST":

        if fark_saat < 0:
            run_days = farkdate.days - 1
            run_hours = 24 + fark_saat
        else:
            run_days = farkdate.days
            run_hours = fark_saat

        microphy = request.form.get("microphy")
        pbl = request.form.get("pbl")
        cumulus = request.form.get("cumulus")
        core = request.form.get("core")  # TODO: include core count

        start_year = sd.split('-')[0]
        start_month = sd.split('-')[1]
        start_day = sd.split('-')[2]
        start_hour = gfs_baslangic_saati
        end_year = ed.split('-')[0]
        end_month = ed.split('-')[1]
        end_day = ed.split('-')[2]
        end_hour = gfs_bitis_saati
        interval_seconds = str(int(isec) * 3600)

        namelist_input_path = WRF_RUN_FOLDER_PATH.joinpath("namelist.input")
        namelist_input_content = render_template(
            "namelists/namelist.input", max_dom=max_dom,
            run_days=str(run_days), run_hours=str(run_hours), run_minutes="00",
            run_seconds="00", start_year=start_year, start_month=start_month,
            start_day=start_day, start_hour=start_hour, end_year=end_year,
            end_month=end_month, end_day=end_day, end_hour=end_hour,
            interval_seconds=interval_seconds, e_we=e_we, e_sn=e_sn, dx=dxdy + "000",
            dy=dxdy + "000", microphy=microphy, cumulus=cumulus, pbl=pbl
        )
        with open(namelist_input_path, 'w') as wps_file:
            wps_file.write(namelist_input_content)

        # TODO: delete old files
        sleep(2)
        is_run_ok = run_repository.run_real_exe()
        if not is_run_ok:
            flash("Please check your WRF configuration.")
            return redirect(url_for(".wrf"))

        print(f"Successfull real.exe run, continuing with wrf.exe with core count: {core}")
        run_log_file_name = f"wrf_run_{datetime.utcnow().strftime(log_time_fmt)}.log"
        # global run_wrf_process
        # process_id = 1
        run_success = run_repository.run_wrf_exe(log_file_name=run_log_file_name, core_count=core)
        if run_success:
            run_repository.move_wrf_outs()
            return redirect(url_for("file_selection_bp.index"))
        else:
            return redirect(url_for("run_wrf_bp.run"))

    else:
        return render_template("run_wrf/wrf.html")


# @run_wrf_bp.route('/output', methods=["GET", "POST"])
# def output():
#     if request.method == "GET":
#
#         return render_template('run_wrf/output.html')
#     else:
#         return send_file("/home/miade/Build_WRF/WRF-4.3-ARW/test/em_real/outputs.zip", as_attachment=True)
#
#
# @run_wrf_bp.route('/download', methods=["GET", "POST"])
# def download():
#     return send_file("/home/miade/Build_WRF/WRF-4.3-ARW/test/em_real/outputs.zip", as_attachment=True)
