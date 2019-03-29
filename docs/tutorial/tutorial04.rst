Part 4: Power Drivers
=====================

Power Drivers are used to control devices with binary states, either on or off. To create a new power driver from an empty template, run:

.. code-block:: console

   $ gardnr new power hello_world_power.py

There should now be a file called `hello_world_power.py` in your current directory. Open this file in your preferred code editor, it should contain:

.. literalinclude:: power_driver_template.py

In the ``on`` method, remove the last two lines and insert:

.. code-block:: python

   print('Device turning on')

In the ``off`` method, remove the last line and insert:

.. code-block:: python

   print('Device turning off')

Your `hello_world_power.py` file should now look like:

.. literalinclude:: hello_world_power.py

Next, add the driver to GARDNR by running:

.. code-block:: console

   $ gardnr add driver hello-world-power power_driver:Power

To run the ``on`` method, run the following command:

.. code-block:: console

   $ gardnr power on hello-world-power

You should now see `Device turning on` displayed in the console. To run the ``off`` method, run the following command:

.. code-block:: console

   $ gardnr power off hello-world-power

You should now see `Device turning off` displayed in the console.

Like sensor and exporter drivers, power drivers can also be scheduled, which is described in :doc:`tutorial03`. However, adding schedules for power drivers requires specifying the state as well. To put turning on a power driver on a schedule, run:

.. code-block:: console

   $ gardnr schedule add hello-world-power every-five-minutes on
