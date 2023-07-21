from flask import Blueprint

run_wrf_bp = Blueprint(
    name="run_wrf_bp",
    import_name=__name__,
    template_folder="./templates",
    static_folder="static",
    url_prefix="/run"
)
