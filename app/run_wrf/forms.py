from datetime import date, timedelta

from flask_wtf import FlaskForm
from wtforms import fields
from wtforms.validators import DataRequired
from wtforms.widgets import NumberInput


class WpsForm(FlaskForm):
    title = "1)   GFS (0.5) verileri indirilir ve ungrib programı çalıştırılır."
    _default_date = date.today() - timedelta(days=1)

    start_date = fields.DateField(
        "start-date", description="Simülasyon Başlangıç Tarihi &nbsp &nbsp &nbsp &nbsp",
        default=_default_date, format="%Y-%m-%d"
    )
    start_hour = fields.RadioField(
        "start-hour", description="Simülasyon Başlangıç Saati &nbsp &nbsp &nbsp",
        choices=[0, 6, 12, 18], default=0)

    end_date = fields.DateField(
        "end-date", description="Simülasyon Bitiş Tarihi &nbsp &nbsp &nbsp &nbsp",
        default=_default_date
    )
    end_hour = fields.RadioField(
        "end-hour", description="&nbsp &nbsp &nbsp Simülasyon Bitiş Saati &nbsp &nbsp",
        choices=[0, 3, 6, 12, 15, 18, 21], default=3
    )
    model_input_interval_in_hours = fields.IntegerField(
        "interval-hours", description="Model Girdi Zaman Aralığı &nbsp",
        default=3, widget=NumberInput(min=1, max=24)  # TODO: add manual validation to unify errors
    )
    model_output_interval_in_minutes = fields.IntegerField(
        "interval-minutes", description="Model Çıktı Zaman Aralığı &nbsp",
        # TODO: add manual validation to unify errors
        # up to 1 day for now
        default=180, widget=NumberInput(min=10, max=60 * 24, step=10)
    )

    def validate(self, extra_validators=None):
        initial_validation = super(WpsForm, self).validate(extra_validators=extra_validators)

        if not initial_validation:
            return False

        _fields_has_errors = False
        # estimate last online available gfs date
        can_go_back_to_date = self._default_date - timedelta(days=9)
        if not self.start_date.data > can_go_back_to_date:
            self.start_date.errors.append(f"Başlangıç tarihi {can_go_back_to_date}'ten büyük olmak zorundadır.")
            _fields_has_errors = True

        # TODO: calculate earliest gfs date _earliest_gfs_date = self._default_date - timedelta(hours=12)
        if self.end_date.data > self._default_date:
            self.end_date.errors.append(f"Bitiş tarihi {self._default_date}'ten küçük olmak zorundadır.")
            _fields_has_errors = True

        # switch to false if fields have errors
        return not _fields_has_errors


class DomainForm(FlaskForm):
    title = "2) Model etki alanını belirleyin."

    grid_resolution = fields.IntegerField(
        "dx-dy-res", description="x ve y doğrultusundaki çözünürlük",
        default=27)
    east_west_grid_count = fields.IntegerField(
        "east-west-grid-count", description="Batı - doğu yönü",
        default=100)
    north_south_grid_count = fields.IntegerField(
        "north-south-grid-count", description="Güney - kuzey yönü",
        default=100)
    ref_lat = fields.FloatField(
        "ref-lat", description="Enlem",
        default=41)
    ref_lon = fields.FloatField(
        "ref-lon", description="Boylam",
        default=29)
    true_lat_1 = fields.FloatField(
        "lambert-true-lat-1", description="1. gerçek enlem",
        default=30)
    true_lat_2 = fields.FloatField(
        "lambert-true-lat-2", description="2. gerçek enlem",
        default=60)

    def validate(self, extra_validators=None):
        initial_validation = super(DomainForm, self).validate(extra_validators=extra_validators)
        if not initial_validation:
            return False

        # TODO: add validation for fields
        # ref_lat must be in range of true lats
        domain_condition = self.true_lat_1.data <= self.ref_lat.data <= self.true_lat_2.data
        if not domain_condition:
            domain_error = f"Seçilen merkez enlem değerler Lambert Conformal için uygun değildir. Lütfen seçtiğiniz "
            self.errors["projection-error"] = domain_error
            return False


class WrfForm(FlaskForm):
    microphy = fields.RadioField(
        "microphy", description="Mikrofizik Süreci Seçin",
        choices=[
            (1, "Kessler"),
            (3, "WSM3"),
            (5, "Ferrier"),
            (4, "WSM5"),
            (2, "Lin"),
            (6, "WSM6")
        ], default=1, validators=[DataRequired()]
    )

    pbl = fields.SelectField(
        "pbl", description="Atmosferik Sınır Tabakası Seçiniz",
        choices=[
            (1, "YSU"),
            (2, "MYJ"),
            (6, "MYNN3"),
            (4, "QNSE-EDMF"),
            (5, "MYNN2"),
            (6, "MYNN3"),
            (7, "ACM2")
        ]
    )
    cumulus = fields.SelectField(
        "cumulus", description="Kümülüs Parametrizasyonu Seçiniz",
        choices=[
            (1, "Kain–Fritsch Scheme"),
            (2, "Betts-Miller-Janjic"),
            (3, "Grell-Freitas"),
            (4, "Old Simplied Arakawa-Schubert"),
            (5, "Grell-3"),
            (6, "Tiedtke")
        ]
    )

    core = fields.SelectField(
        "core", description="Kaç Çekirdek ile Paralel Çalışacağını Seçiniz",
        choices=list(range(1, 7)), default=2)
