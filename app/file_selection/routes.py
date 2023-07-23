from flask import render_template, request, redirect, url_for, current_app, session

from app import FlaskApp
from app.WrfOutManager import WrfOutManager
from app.file_selection import file_selection_bp
from app.file_selection.forms import SelectFileForm

current_app: FlaskApp


@file_selection_bp.route("/", methods=["GET", "POST"])
def index() -> str:
    form = SelectFileForm()
    if request.method == "POST":
        selected_file = form.selected_file.data
        # TODO: use session to keep track of the selected file name, after fixing the session flushing bug...
        return redirect(url_for(".summary", wrf_out_file=selected_file))

    return render_template("file_selection/forms/select_file.html", form=form)


@file_selection_bp.route("/<string:wrf_out_file>/summary")
def summary(wrf_out_file: str) -> str:
    wrf_manager: WrfOutManager = current_app.wrf_manager

    wrf_manager.read_dataset(wrf_out_file)
    summary_data = wrf_manager.summarize_dataset()
    wrf_manager.close_dataset()

    session['selected_file'] = wrf_out_file
    return render_template("file_selection/summary.html", selected_file=wrf_out_file, current_file_summary=summary_data)

