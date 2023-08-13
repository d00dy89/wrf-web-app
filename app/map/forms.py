from typing import List, Tuple

from flask_wtf import FlaskForm
from wtforms import fields
from wtforms import SelectField

import app.map.constants as Constants


class SurfacePlotForm(FlaskForm):
    should_plot_slp = fields.BooleanField(label="Eş Yüzey Basınç Konturları (hPa)", default="checked")
    should_plot_wind = fields.BooleanField(label="10 metre Rüzgar Barbları (m/s)", default="checked")
    colour_fill_data = fields.SelectField(
        label="Değişken Seç:",
        choices=[
            (Constants.FIELD_KEY_T2, "Sıcaklık 2m"),
            (Constants.FIELD_KEY_TD2, "Çiy Noktası 2m"),
            (Constants.FIELD_KEY_RH2, "Bağıl Nem 2m"),
            (Constants.FIELD_KEY_WIND_10, "Rüzgar 10m"),
            (Constants.FIELD_KEY_PREC, "Yağış"),
            (Constants.FIELD_KEY_SNOW, "Kar")
        ],
        default=Constants.FIELD_KEY_T2)


class TimeSelectionForm(FlaskForm):
    __default_timeidx = 0
    select_time = SelectField(label="Zaman Adımı Seç:", id='date-time', default=__default_timeidx)

    def __init__(
            self,
            available_times: List[Tuple[int, str]],
            *args, **kwargs) -> None:
        super(TimeSelectionForm, self).__init__(*args, **kwargs)
        choices = [(date[0], date[1].strftime('%Y-%m-%d %H:%M:%S')) for date in available_times]
        self.select_time.choices = choices
        # self.select_time.data = choices[selected_time_index][1] if selected_time_index else choices[0][1]
