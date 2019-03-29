```
 #####      #     ######   ######   #     #  ######
#     #    # #    #     #  #     #  ##    #  #     #
#         #   #   #     #  #     #  # #   #  #     #
#  ####  #     #  ######   #     #  #  #  #  ######
#     #  #######  #   #    #     #  #   # #  #   #
#     #  #     #  #    #   #     #  #    ##  #    #
 #####   #     #  #     #  ######   #     #  #     #
```

Bootstrapper for DIY IoT projects with a focus on horticulture.

# Documentation

[https://gardnr.readthedocs.io](https://gardnr.readthedocs.io)

# Drivers

Here are some provided driver modules:

- [Sensor](https://github.com/search?q=org%3Agardnr+topic%3Asensor)
- [Exporter](https://github.com/search?q=org%3Agardnr+topic%3Aexporter)
- [Power](https://github.com/search?q=org%3Agardnr+topic%3Apower)

# Development

## Building Documentation

Documentation is stored in the `docs` directory in [reStructedText](http://docutils.sourceforge.net/rst.html) and built using [Sphinx](http://www.sphinx-doc.org). To build the documentation HTML pages, run:

`$ sphinx-build -b html docs docs/build`

To view the built documentation, open a browser to `docs/build/index.html` in repository.
