Hello World
===========

Here are instructions for creating the simplest drivers. Familiarize yourself with GARDNR definitions before going through this tutorial. See :doc:`definitions`.

The basic features of GARDNR are logging metrics to the database, exporting metric logs, and writing to the log file. The following source code contains code for a sensor driver (read) and an exporter driver (write). We will start with the simplest driver possible:

.. literalinclude:: hello_world.py

Next, add the metric and drivers to GARDNR. Run the following commands in the repository root directory:

.. code-block:: console

   $ python3 -m gardnr.cli add metric hello-world air notes
   $ python3 -m gardnr.cli add driver hw-sensor samples.hello_world:HelloWorldSensor -c first=Hello second='World!'
   $ python3 -m gardnr.cli add driver hw-exporter samples.hello_world:HelloWorldExporter

You can then run the driver with the following command:

.. code-block:: console

   $ python3 -m gardnr.cli read

This will write a value of `Hello World!` for metric `hello-world` into `gardnr.db` and write a log message to `gardnr.log`. You can verify the metric value was successfully writen to `gardnr.db` using the `SQLite CLI`_. You can verify the log message was written `gardnr.log` by running :code:`$ tail -n 10 gardnr.log`

.. _SQLite CLI: https://www.sqlite.org/cli.html

To run the test exporter, run the following command:

.. code-block:: console

   $ python3 -m gardnr.cli write

All this test exporter does is print the metric value to the console and write to `gardnr.log`, so you should see `Hello World!`.

Now lets add a manually tracked metric:

.. code-block:: console

   $ python3 -m gardnr.cli manual on hello-world

Because the metric `hello-world` has been set to manual, it will appear in the Log Entry System web client. Refer to the README for instructions on using L.E.S.

Congratulations! You are now ready to create your own drivers for fulfilling your monitoring and automation needs. Use the driver code in the `samples` directory for examples of production drivers.
