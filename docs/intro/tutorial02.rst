Tutorial Part 2
===============

Manual Log Entry
----------------

In :doc:`tutorial01` you created a driver which wrote logs for an air temperature metric, `hello-world`. For some metrics, you not have the sensor hardware available to read metric data so there will be no driver code to write to log metric data. Or, sensor hardware may fail and your driver code unable to log metric data. In these cases, you will want to manually log your metric data. To set a metric to manual mode, run:

.. code-block:: console

   $ gardnr manual on hello-world

Manual metrics will be displayed on the Log Entry System. The Log Entry System is part of the GARDNR web server, to start it run:

.. code-block:: console

   $ gardnr-server -b 0.0.0.0:5000

Next, open http://localhost:5000 in a browser. You should see a text field to enter a value for the `hello-world` metric. After you entered a number into the text field, hit the Submit buttom to log the value.

Continue to :doc:`tutorial03`
