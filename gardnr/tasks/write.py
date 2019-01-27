from typing import List

import peewee

from gardnr import constants, drivers, logger, models


def _exported_logs(driver_model: models.Driver) -> peewee.ModelSelect:
    """Helper function to get the export logs associated with a driver"""

    return models.ExportLog.select(models.ExportLog.metric_log.id)\
        .join(models.MetricLog)\
        .where(models.ExportLog.driver == driver_model)


def get_all_logs(driver_model: models.Driver) -> peewee.ModelSelect:
    """All logs that have not been exported with driver_model"""

    return models.MetricLog.select().where(
        models.MetricLog.id.not_in(_exported_logs(driver_model))
    )


def get_whitelisted_logs(
        driver_model: models.Driver,
        whitelist: List[str]
) -> peewee.ModelSelect:
    """
    Logs from whitelisted metrics that have not been exported with
    driver_model
    """

    return models.MetricLog.select()\
        .join(models.Metric)\
        .where(models.MetricLog.id.not_in(_exported_logs(driver_model))
               & models.MetricLog.metric.type.in_(whitelist))


def get_not_blacklisted_logs(
        driver_model: models.Driver,
        blacklist: List[str]
) -> peewee.ModelSelect:
    """
    Logs from whitelisted metrics that have not been exported with
    driver_model
    """

    return models.MetricLog.select()\
        .join(models.Metric)\
        .where(models.MetricLog.id.not_in(_exported_logs(driver_model))
               & models.MetricLog.metric.type.not_in(blacklist))


def write(exporters: List[drivers.Exporter]) -> None:
    """Upload logs in local DB to web server."""

    for exporter in exporters:

        if exporter.whitelist:
            logs = get_whitelisted_logs(exporter.model, exporter.whitelist)
        elif exporter.blacklist:
            logs = get_not_blacklisted_logs(exporter.model, exporter.blacklist)
        else:
            logs = get_all_logs(exporter.model)

        # no new logs to export
        if not logs:
            continue

        # store the failed logs during export
        failed_log_ids = []  # type: List[UUID]

        try:
            exporter.export([log for log in logs])  # type: ignore
        except Exception as e:  # pylint: disable=broad-except
            logger.exception('Error transmitting')

            # If the exporter sets the failed_logs field in the exception
            # use it, otherwise assume all logs failed
            failed_logs = getattr(e, 'failed_logs', [])

            # If there are no failed logs specified, skip export logging
            if not failed_logs:
                continue

            failed_log_ids = [log.id for log in failed_logs]

        for log in logs:
            if log.id in failed_log_ids:
                continue

            models.ExportLog.create(metric_log=log, driver=exporter.model)
