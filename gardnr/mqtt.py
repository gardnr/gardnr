#!/usr/bin/env python

from typing import Dict, Optional

from paho.mqtt import subscribe
from paho.mqtt.client import Client, MQTTMessage

from gardnr import logger, metrics, models


def main() -> None:
    models.initialize_db()

    # check every topic to get any metric name
    subscribe.callback(consume_message, '#')


def consume_message(
        client: Client,
        userdata: Optional[Dict],
        message: MQTTMessage
) -> None:
    metric_name = message.topic

    metric = models.Metric.get_or_none(
        models.Metric.name == metric_name)

    if not metric:
        logger.warning('unknown metric "{}"'.format(metric_name))
        return

    metrics.create_metric_log(metric_name, message.payload)


if __name__ == '__main__':
    main()
