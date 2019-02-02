Drivers
=======

`Driver` is an abstract base class for creating runnable tasks. `Driver` is inherited into three primary types: :ref:`sensor`, :ref:`power`, and :ref:`exporter`. Note that these three types are also abstract base classes and should always be inherited from when making custom drivers.


Management
----------

- See :doc:`intro/tutorial01` for how to add drivers
- To remove a driver `$ python3 -m gardnr.cli remove driver my-driver`
- To disable a driver `$ python3 -m gardnr.cli disable driver my-driver`. Disabling a driver will prevent it from executing during a read.


.. _sensor:

Sensor
-------


.. _power:

Power
-----


.. _exporter:

Exporter
---------
Exporters are given a list of logs and are responsible for sending the log data to desired out-of-system destinations. These destinations could include a cloud service that uses a web API to receive data, or a CSV file. Exporters can filter the types of logs that get sent to them using the metric whitelist and blacklist. `whitelist` is a list of metric types that are acceptable to the driver, `blacklist` is a list of metric types that are unacceptable to the driver. Use the one that is more convienent i.e. requires less values need. If both `whitelist` and `blacklist` are specified, only `whitelist` will be used. If neither is specified, all metric types will be sent.

**Error Handling**
Because exporters may interact with external systems, there is a chance that exporting logs will fail. If an exception is raised during exporting, all the logs being exported are marked as failed. If some of the logs succeeded and some failed, the `failed_logs` attribute can be set on the raised exception to only mark certain logs as failed.


.. _installation:

Installation
------------
Drivers are installed through the `add driver` command. Each driver is given a name which allows for multiple drivers using the same source code file. Recommended driver installation include creating a `README` and `install.sh` file to go along with the source code file.
