setuptools-epydoc
=================

A setuptools command to trigger the epydoc API documentation generator.

Author: Johannes Wienke <languitar@semipol.de>

Usage
-----

In your `setup.py` require this package as a setup dependency:

```
setup(...
      setup_requires=['setuptools-epydoc'],
      ...)
```

Afterwards you can call `python setup.py epydoc` to generate the documentation.

Also have a look at `python setup.py epydoc -h` for further options.
