from flask import Flask
from flask import render_template
from flask_session import Session

from config import Config

from app.run_wrf import run_wrf_bp
from app.WrfOutManager import WrfOutManager


class FlaskApp(Flask):
    wrf_manager: WrfOutManager

    def __init__(self, *flask_args, **flask_kwargs) -> None:
        # noinspection PyArgumentList
        super().__init__(__name__, *flask_args, **flask_kwargs)
        self.config.from_object(Config)
        Session(self)

        _path_config = self.config.get("PATH_CONFIG")
        self.wrf_manager = WrfOutManager(
            path_config=_path_config
        )


def create_flask_app() -> FlaskApp:

    app = FlaskApp()
    logger = app.logger
    logger.debug(f"Initialized app: {app.name}")

    @app.route("/")
    def index():
        return render_template('index.html')

    with app.app_context():
        from app.run_wrf import run_wrf_bp, routes as _
        from app.file_selection import file_selection_bp, routes as _
        from app.map import map_bp, routes as _

    app.register_blueprint(run_wrf_bp)
    app.register_blueprint(file_selection_bp)
    app.register_blueprint(map_bp)
    return app
