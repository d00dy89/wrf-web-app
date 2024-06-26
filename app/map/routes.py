from datetime import datetime

from flask import render_template, session, url_for, redirect, current_app

from app import FlaskApp
from app.file_selection.forms import SelectFileForm
from app.file_selection.routes import selected_file_arg
from app.map import map_bp
from app.WrfOutManager import WrfOutManager
from app.map.forms import SurfacePlotForm, TimeSelectionForm

from library.plotting.CartopyMPLPlotter import CartopyMplPlotter

from app.path_config import PathConfig

import app.map.constants as Constants

current_app: FlaskApp
path_config: PathConfig = current_app.config.get("PATH_CONFIG")
wrf_manager: WrfOutManager = current_app.wrf_manager
plotter = CartopyMplPlotter(wrf_data_manager=wrf_manager)


@map_bp.route("/", methods=["GET", "POST"])
def index() -> str:
    select_file_form = SelectFileForm()

    selected_file = session.get(selected_file_arg, None)
    if selected_file is None:
        return redirect(url_for('file_selection_bp.index'))

    wrf_manager.read_dataset(selected_file)

    form = SurfacePlotForm()
    should_plot_slp = form.should_plot_slp.data
    should_plot_wind = form.should_plot_wind.data
    colour_fill_data = form.colour_fill_data.data

    time_form = TimeSelectionForm(
        available_times=wrf_manager.data.available_times
    )
    selected_time = int(time_form.select_time.data)
    wrf_manager.load_base_variables()

    st = datetime.utcnow()
    print('Creating Figure...')

    plotter.create_figure()
    plotter.generate_figure_title(timeidx=selected_time)

    # TODO: provide an interface for contour customization
    if should_plot_slp and (colour_fill_data is not Constants.FIELD_KEY_SLP):
        if colour_fill_data == Constants.FIELD_KEY_GEO500:
            plotter.plot_contour(data_key=colour_fill_data, time_step=selected_time)
        elif colour_fill_data == Constants.FIELD_KEY_TEMP850:
            plotter.plot_contour(data_key=colour_fill_data, time_step=selected_time, level=[0], line_color="black", line_style="dashed", line_width=3)
            plotter.plot_contour(data_key=Constants.FIELD_KEY_RH850, time_step=selected_time, cmap="rainbow_r")

        elif colour_fill_data == Constants.FIELD_KEY_RH700:
            plotter.plot_contour(data_key=colour_fill_data, time_step=selected_time)

        elif colour_fill_data == Constants.FIELD_KEY_WS300:
            plotter.plot_contour(data_key=Constants.FIELD_KEY_SLP, time_step=selected_time, line_style="dashed")

        else:
            plotter.plot_contour(data_key=Constants.FIELD_KEY_SLP, time_step=selected_time)

    # TODO: provide an interface for barb customization
    if should_plot_wind:
        plotter.plot_wind(wind_variable_key=colour_fill_data, time_step=selected_time, grid_interval=5)

    plotter.plot_contour_fill(data_key=colour_fill_data, timeidx=selected_time)

    plotter.plot_figure_title()
    plotter.plot_gridlines()

    image_src = plotter.save()
    wrf_manager.close_dataset()
    et = datetime.utcnow()
    print(f"Creating Figure took: {(et - st).total_seconds()}")
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
    return redirect(url_for('.index', selected_file=selected_file))
