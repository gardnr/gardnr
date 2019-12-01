Driver Configuration
====================

Driver configuraiton is used to make ``Driver`` classes more re-usable. Instead of hardcoding attributes into a class, you can have the attribute loaded at run-time into the driver instance. For example, imagine you have a sensor driver class:

.. literalinclude:: hardcoded_sensor.py

Instead of using the string literal, ``'hello world'``, an attributes can be used instead:

.. literalinclude:: attribute_sensor.py

Now, to set the the ``message`` attribute, we pass in a value while adding the driver class to GARDNR

.. code-block:: console

   $ gardnr add driver sensor attribute_sensor:Sensor -c message="hello world"

Multiple configuration attributes
---------------------------------

Multiple configuration attributes can be passed in while adding a driver to GARDNR

.. clode-block:: console

   $ gardnr add driver sensor attribute_sensor:Sensor -c attr1=55 attr2="foo"
