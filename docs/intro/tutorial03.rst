Tutorial Part 3
===============

Scheduling
----------

Sensor and exporter drivers can be executed manually using the `read` and `write` commands respectively:

.. code-block:: console

   $ gardnr read  # executes sensor drivers
   $ gardnr write # extutes exporter drivers

This can be tedious and inconvenient to manually run commands in a shell to execute driver code. Schedules can be used to automatically execute drivers. First a schedule must be created. Schedules can be added to GARDNR using `CRON <https://en.wikipedia.org/wiki/Cron>`_ syntax.

.. code-block:: console

   $ gardnr add schedule every-five-minutes \*/5 \* \* \* \*
   You entered: Every 5 minutes
   Does this look correct? ([y]/n)

Note that the `\*` is to escape the astericks so it is not evaluated by the shell as a wildcard. The command above will add a schedule named `every-five-minutes` after you confirm by hitting `y` and then `Enter`. Next, schedule a driver. We will schedule the `hello-world-sensor` we created in :doc:`tutorial01`:

.. code-block:: console

   $ gardnr schedule add hello-world-sensor every-five-minutes

To execute scheduled drivers, enter the following command which will run indefinitely:

.. code-block:: console

   $ gardnr-automata

Continue to :doc:`tutorial04`
