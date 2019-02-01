Quickstart
===========

GARDNR requires Python 3.5 or higher.

Be sure to famliarize yourself with Object-oriented programming and [Python classes](https://docs.python.org/3.5/tutorial/classes.html) before using GARDNR.

First, install GARDNR using [pip](https://pip.pypa.io/en/stable/):

.. code-block:: console

   $ pip install gardnr

The basic features of GARDNR are logging metrics to the database and exporting metric logs. To start logging a metric, you first must add the metric to the database, like so:

.. code-block:: console

   $ gardnr add metric air notes hello-world

Next, a sensor driver can be added which can create logs for the metric `hello-world`. The sensor driver code must be implemented before it can be added to the database. GARDNR can generate empty templates of driver classes to be able to write them faster.

.. code-block:: console

   $ gardnr new sensor hello_world_sensor.py

There should now be a file called `hello_world_sensor.py` in your current directory. Open this file in your preferred code editor, it should contain:

.. literalinclude:: sensor_driver_template.py

At the end of the file, remove the last two lines and insert:

.. code-block:: python
   
   metrics.create_metric_log('hello-world', 'Hello, World!')

Be sure to indent the line above by eight spaces so it is properly nested under the `read` method. Your `hello_world_sensor.py` file should now look like:

.. literalinclude:: hello_world_sensor.py

Next, the sensor driver module must be added to GARDNR's system. To do this, run the following command:

.. code-block:: console
   $ gardnr add driver hello-world hello_world_sensor:Sensor

The sensor driver module you just added to GARDNR can now be executed using the following command:

.. code-block:: console
   $ gardnr read

What running the command above does is create a log for our `hello-world` metric. Now we can add an exporter driver to GARDNR. Exporters allow logs to be sent to external locations.. In this case, the log will simply be printed to the console for demostration purposes. First, start with an empty exporter template:

.. code-block:: console
   $ gardnr new exporter hello_world_exporter.py

Next, open `hello_world_exporter.py` in your preferred code editor, it should contain:

.. literalinclude:: exporter_driver_template.py

At the end of the file, remove the last two lines and insert:

.. code-block:: python
   
   print(log.value)

Be sure to indent the line above by 12 spaces so it is properly nested under the `for` loop inside the `export` method. Your `hello_world_sensor.py` file should now look like:

.. literalinclude:: hello_world_exporter.py

The exporter driver module you just added to GARDNR can now be executed using the following command:

.. code-block:: console
   $ gardnr write

You should now see `Hello, World!` displayed in the console. Note, that if you the above command again, nothing would be displayed. This is because metric logs are only exported once per exporter in the system.
