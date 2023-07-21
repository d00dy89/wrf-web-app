from flask import Blueprint, current_app

map_bp = Blueprint(
    name="map_bp",
    import_name=__name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/map"
)

