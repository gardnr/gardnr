import os
import pathlib
from typing import Any, Tuple

from flask import Flask, redirect, render_template, request
from flaskcommand import flask_command
from flask_wtf import FlaskForm, csrf
from wtforms import Field, FileField, FloatField, IntegerField, TextAreaField
from wtforms.validators import Optional as OptionalValidator

from gardnr import constants, metrics, models, settings

app = Flask(__name__)
app_csrf = csrf.CSRFProtect(app)

app.config.update(dict(
    SECRET_KEY='\xc1\x7f;\xbb:\xe6P\xbf0\xa1\x91\xd5X|\xfa\xd4"AZ\xe1/\xe1tt',
    WTF_CSRF_SECRET_KEY='h\xca\xe8\x16>\xae\xd1m\xf9)\xec\xef\x03\x18\xf8\x8d'
))

models.initialize_db()
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)

FIELD_NAME_DELIMITER = ':'

main = flask_command(app)


@app.route('/', methods=('GET', 'POST'))
def manual_logs():
    class MetricForm(FlaskForm):
        """
        Anonymous Form class for constructing
        personalizated forms based on sensors configured
        """
        pass

    # pylint: disable=singleton-comparison
    manual_metrics = models.Metric.select().where(
        (models.Metric.manual == True) &  # noqa: E712
        (models.Metric.disabled == False))

    for metric in manual_metrics:
        metric_field = get_field(metric)

        setattr(MetricForm, metric.name, metric_field)

    # magically populates the form from the request :)
    metric_form = MetricForm()

    # save form
    if metric_form.validate_on_submit():
        for field_name, field_value in metric_form.data.items():
            if field_name == 'csrf_token':
                continue
            if not field_value:
                continue

            metric = models.Metric.get(models.Metric.name == field_name)

            if(metric.type == constants.IMAGE and
               field_value.filename == ''):
                continue

            create_log(metric, field_value)

        return redirect('/')

    return render_template('log_form.html', form=metric_form)


def get_field(metric: models.Metric) -> Field:

    if metric.type == constants.T9E:
        return FloatField(metric.name, validators=[OptionalValidator()])
    elif metric.type == constants.HUMIDITY:
        return IntegerField(metric.name, validators=[OptionalValidator()])
    elif metric.type == constants.IMAGE:
        return FileField(metric.name, validators=[OptionalValidator()])
    elif metric.type == constants.NOTES:
        return TextAreaField(metric.name, validators=[OptionalValidator()])
    elif metric.type == constants.PH:
        return FloatField(metric.name, validators=[OptionalValidator()])
    elif metric.type == constants.EC:
        return FloatField(metric.name, validators=[OptionalValidator()])

    raise ValueError('field type "{field_type}" not found'.format(
        field_type=metric))


def create_log(metric: models.Metric,
               field_value: Any) -> models.MetricLog:

    if metric.type == constants.IMAGE:
        extension = pathlib.Path(field_value.filename).suffix
        image_blob = field_value.read()
        # type: ignore
        return metrics.create_file_log(metric.name, image_blob, extension)

    value = metrics.standardize_metric(metric.type, field_value)

    return metrics.create_metric_log(metric.name, value)
