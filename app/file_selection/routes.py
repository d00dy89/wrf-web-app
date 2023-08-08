from flask import render_template, request, redirect, url_for, current_app, session

from app import FlaskApp
from app.WrfOutManager import WrfOutManager
from app.file_selection import file_selection_bp
from app.file_selection.forms import SelectFileForm

current_app: FlaskApp
logger = current_app.logger
selected_file_arg = "SELECTED_WRFOUT_FILE"


@file_selection_bp.route("/", methods=["GET", "POST"])
def index() -> str:
    # Use it to change selected file
    form = SelectFileForm()
    if request.method == "POST":
        selected_file = form.selected_file.data
        # TODO: use session to keep track of the selected file name, after fixing the session flushing bug...
        session[selected_file_arg] = selected_file
        return redirect(url_for(".summary"))

    return render_template("file_selection/index.html", form=form)


@file_selection_bp.route("/change", methods=["POST"])
def change_file():
    new_file = request.form.get("selected_file_select_field")
    _ = session.pop(selected_file_arg)
    session[selected_file_arg] = new_file
    return redirect(url_for("map_bp.index"))


@file_selection_bp.route("/summary")
def summary() -> str:
    wrf_manager: WrfOutManager = current_app.wrf_manager
    try:
        wrf_out_file = session.get(selected_file_arg)
    except Exception as e:
        logger.warning(f"Could not find {selected_file_arg} in session. Details: {e}")
        return redirect(url_for(".index"))

    wrf_manager.read_dataset(wrf_out_file)
    summary_data = wrf_manager.summarize_dataset()
    wrf_manager.close_dataset()

    return render_template("file_selection/summary.html", current_file_summary=summary_data, selected_file=wrf_out_file)

