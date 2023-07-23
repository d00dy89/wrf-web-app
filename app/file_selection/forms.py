import os

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField
from wtforms.validators import DataRequired

from app import FlaskApp
from path_config import PathConfig

current_app: FlaskApp = current_app
path_config: PathConfig = current_app.config.get("PATH_CONFIG")


class SelectFileForm(FlaskForm):
    selected_file = RadioField(
        label='Select a File',
        validators=[DataRequired()]
    )
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_file.choices = os.listdir(path_config.WRF_OUTPUT_FOLDER_PATH)
