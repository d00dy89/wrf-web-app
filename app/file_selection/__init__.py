from flask import Blueprint

file_selection_bp = Blueprint(
    name="file_selection_bp",
    import_name=__name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/files"
)
