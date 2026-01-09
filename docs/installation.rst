Installation
============

Requirements
------------

* Python 3.8 or higher
* pip (Python package installer)

Install from PyPI
-----------------

The easiest way to install Chanda is using pip:

.. code-block:: bash

   pip install chanda

Install from Source
-------------------

To install the latest development version:

.. code-block:: bash

   git clone https://github.com/hrishikeshrt/chanda.git
   cd chanda
   pip install -e .

This installs the package in "editable" mode, allowing you to modify the code and see changes immediately.

Optional Dependencies
---------------------

For Development
~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -e ".[dev]"

This includes:

* pytest - Testing framework
* pytest-cov - Code coverage
* black - Code formatting
* flake8 - Code linting
* mypy - Type checking

For Documentation
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -e ".[docs]"

This includes:

* sphinx - Documentation generation
* sphinx-rtd-theme - ReadTheDocs theme
* sphinx-autodoc-typehints - Type hint documentation

For Web Application
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -e ".[webapp]"

This includes Flask and related dependencies for the web interface.

Verify Installation
-------------------

Check that the installation was successful:

.. code-block:: bash

   chanda --version

Test basic functionality:

.. code-block:: python

   python -c "from chanda import identify_meter; print(identify_meter('धर्मक्षेत्रे कुरुक्षेत्रे')['display_chanda'])"

Troubleshooting
---------------

Levenshtein Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On some systems, ``python-Levenshtein`` may require compilation. If you encounter errors:

**Ubuntu/Debian:**

.. code-block:: bash

   sudo apt-get install python3-dev
   pip install python-Levenshtein

**macOS:**

.. code-block:: bash

   xcode-select --install
   pip install python-Levenshtein

**Windows:**

Install Microsoft C++ Build Tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/

Data Files Not Found
~~~~~~~~~~~~~~~~~~~~

If you get "FileNotFoundError" for CSV files:

.. code-block:: bash

   pip install --force-reinstall chanda
