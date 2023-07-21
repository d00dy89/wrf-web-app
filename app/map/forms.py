from flask_wtf import FlaskForm
from wtforms import fields
from wtforms import IntegerField, SelectField, FloatField, StringField, RadioField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets import ColorInput, CheckboxInput

VAR_KEYS = ["slp", "T2", "T"]
# slp, t2, td2, rh2, mdbz, rain, ws10, wd10, ter, mcape
FIELD_SLP = "slp"
FIELD_T2 = "T2"
FIELD_TD2 = "td2"
FIELD_RH2_SFC = "rh2"
FIELD_MAX_DBZ = "mdbz"
FIELD_PREC = "rainh"


class SurfacePlotForm(FlaskForm):
    should_plot_slp = fields.BooleanField(label="SLP", default="checked")
    should_plot_wind = fields.BooleanField(label="Wind 10m", default="checked")
    colour_fill_data = fields.SelectField(
        label="Select Variable",
        choices=["T2", "td2", "rh2", "mdbz", "rain", "snow"],
        default="T2")


class VariableSelectionForm(FlaskForm):
    variable_key = SelectField(label="select variable", validators=[DataRequired()], default='slp')

    def __init__(self,
                 available_variable_keys: (str, ...),
                 *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.variable_key.choices = available_variable_keys


class VerticalInterpolationForm(FlaskForm):
    interpolate_by = SelectField(label="Interpolate with")
    interpolate_to_level = FloatField(label="Interpolate to level", validators=[NumberRange(0, 1000)])

    def __init__(self,
                 interpolate_by_choices: (str, ...) = ("p", "z"),
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interpolate_by.choices = interpolate_by_choices


class MapFeatureForm(FlaskForm):
    feature_type = SelectField(label="Select Plot Feature", choices=["contour", "fill", "barb", "arrow"],
                               validators=[DataRequired()])


class ContourConfigurationForm(FlaskForm):
    line_widths = SelectField(
        label="Line Thickness",
        choices=list(range(1, 20)),
        default=2)
    line_color = StringField(
        label="Line Color",
        widget=ColorInput()
    )
    labels_on = RadioField(label="Label On")


class TimeSelectionForm(FlaskForm):
    __default_timeidx = 0
    time_index = IntegerField(label='Time Index', default=__default_timeidx)
    select_time = SelectField(label='Select Time Step', id='date-time')

    def __init__(
            self,
            available_times,
            selected_time: int = __default_timeidx,
            *args, **kwargs) -> None:
        super(TimeSelectionForm, self).__init__(*args, **kwargs)
        self.select_time.choices = [date.get('date').strftime('"%Y-%m-%d %H:%M:%S"') for date in available_times]
        self.select_time.data = selected_time if selected_time else self.select_time.choices[0]
        self._set_time_index()

    def _set_time_index(self):
        self.time_index.data = self._get_time_index()

    def _get_time_index(self) -> int:
        return self.select_time.choices.index(self.select_time.data)
