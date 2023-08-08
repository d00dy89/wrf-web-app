import os

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired

from app import FlaskApp
from app.path_config import PathConfig

current_app: FlaskApp = current_app
path_config: PathConfig = current_app.config.get("PATH_CONFIG")


class SelectFileForm(FlaskForm):
    selected_file = RadioField(
        label='Select File',
        validators=[DataRequired()]
    )
    selected_file_select_field = SelectField(label="Select File")
    submit = SubmitField("Dosya Seç")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_files = os.listdir(path_config.WRF_OUTPUT_FOLDER_PATH)
        self.selected_file.choices = sorted(available_files)
        self.selected_file_select_field.choices = sorted(available_files)

