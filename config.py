import os

from path_config import PathConfig

# load from env and provide defaults
_debug = os.environ.get('DEBUG', False)
_host = os.environ.get('HOST', '127.0.0.1')
_port = os.environ.get('PORT', '5000')
_schema = os.environ.get("SCHEMA", "http")


class Config:
    """ Flask config """
    DEBUG = _debug
    SECRET_KEY = "really-secret-key"  # uuid.uuid4().hex
    SERVER_NAME = f"{_host}:{_port}" if int(_port) > 0 else f"{_host}"
    PREFERRED_URL_SCHEME = _schema
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_REFRESH_EACH_REQUEST = False

    PATH_CONFIG = PathConfig()
