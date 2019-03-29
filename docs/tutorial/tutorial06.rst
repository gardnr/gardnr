Part 6: Triggers and Grow Recipes
=================================

Triggers are a way to automatically change the state of a power driver based on the rules defined in a grow recipe. In order for triggers to be enabled, there must be an active grow, explained in :doc:`tutorial05`, as well as a grow recipe file configured. Grow recipes are stored in an XML files and adhere to the `Grow Recipe Schema <https://grow-recipe-schema.readthedocs.io>`_.

To start, create a very simple grow recipe in a text editor:

.. literalinclude:: hello-world-recipe.xml
   :language: xml

Save this file as `hello-world-recipe.xml`. Next, configure GARDNR to use the recipe you just created by adding it to the settings. Open a new blank file in a text editor and add:

.. literalinclude:: recipe_settings_local.py

Save the file as `settings_local.py`.

Next, add a trigger on the `hello-world` metric we created in :doc:`tutorial01` when it reaches the max temperature we specified in the grow recipe, it turns on the `hello-world-power` driver specified in :doc:`tutorial04`. To add the trigger, run:

.. code-block:: console

   $ gardnr add trigger hello-world max hello-world-power on

Triggers are checked on a special schedule when ``gardnr-automata`` is run. To test, make sure ``gardnr-automata`` is running and run a ``gardnr read`` command to log a metric value of 20 for the `hello-world` metric. Within five minutes, you should see 'Device turning on` appear in the console running ``gardnr-automata`` because a temperature of 20 exceeds the max threshold of 18 for the air temperature metric `hello-world`, specified in the grow recipe.

Congratulations! You now know all of the core features GARDNR has to offer. Now you can start writing drivers which interface with actual hardware devices and data stores. Some out-of-the-box drivers are available on `GitHub <https://github.com/gardnr>`_ with instructions on setting up the hardware.
