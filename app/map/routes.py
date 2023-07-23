import os

from flask import render_template, session, url_for, redirect, request, current_app

from app import FlaskApp
from app.map import map_bp
from app.WrfOutManager import WrfOutManager
from app.file_selection.forms import SelectFileForm
from app.map.forms import SurfacePlotForm, TimeSelectionForm

from library.plotting.CartopyMPLPlotter import CartopyMplPlotter, PlotKwargs

from path_config import PathConfig


current_app: FlaskApp
path_config: PathConfig = current_app.config.get("PATH_CONFIG")
wrf_manager: WrfOutManager = current_app.wrf_manager
plotter = CartopyMplPlotter(wrf_data_manager=wrf_manager)


@map_bp.route("/", methods=["GET", "POST"])
def index() -> str:
    # TODO: fix session
    selected_file = session.get("selected_file", None)
    if selected_file is None:
        return redirect(url_for('file_selection_bp.index'))
    # TODO: give an options window instead of directly creating map
    return redirect(url_for('.create_map', selected_file=selected_file))


@map_bp.route("/<string:selected_file>", methods=["GET", "POST"])
def create_map(selected_file: str) -> str:
    session['selected_file'] = selected_file
    wrf_manager.read_dataset(selected_file)

    select_file_form = SelectFileForm()

    form = SurfacePlotForm()

    selected_time = request.form.get("select_time")
    time_form = TimeSelectionForm(
        available_times=wrf_manager.get_available_times(),
        selected_time=selected_time
    )
    time_step = time_form.time_index.data
    should_plot_slp = form.should_plot_slp.data
    should_plot_wind = form.should_plot_wind.data
    colour_fill_data = form.colour_fill_data.data

    wrf_manager.load_base_variables()

    plotter.create_figure()

    if should_plot_slp:
        print("plotting slp")
        plotter.plot_slp(time_step=time_step)

    if should_plot_wind:
        plotter.plot_wind(time_step=time_step, grid_interval=10)

    plotter.plot_contour_fill(data_key=colour_fill_data, timeidx=time_step)

    image_src = plotter.save()
    wrf_manager.close_dataset()
    return render_template(
        "map/index.html",
        form=form,
        time_form=time_form,
        select_file_form=select_file_form,
        selected_file=selected_file,
        image_source=image_src)


@map_bp.route("/<string:selected_file>/clear")
def clear_map(selected_file: str):
    plotter.clear_figure()
    return redirect(url_for('.create_map', selected_file=selected_file))
