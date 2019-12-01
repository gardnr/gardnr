Part 7: MQTT
=================================

GARDNR comes with a built-in `MQTT <http://mqtt.org>`_ subscriber for logging metrics. In order to use the subscriber, it must be connected to a broker, such as `Mosquitto <https://mosquitto.org>`_.

Use the metric name as the topic and the log value as the message.

To start the MQTT subscriber, run ``gardnr-mqtt``
