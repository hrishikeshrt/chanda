Chanda - Sanskrit Meter Identification
======================================

**Chanda** is a comprehensive Python library for identifying and analyzing Sanskrit poetic meters (छन्द).

.. image:: https://badge.fury.io/py/chanda.svg
   :target: https://badge.fury.io/py/chanda
   :alt: PyPI version

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.8+

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

Features
--------

* **200+ Meter Database**: Comprehensive coverage of Sanskrit meters

  * Sama-vṛtta (meters with identical padas)
  * Ardhasama-vṛtta & Viṣama-vṛtta (meters with varying padas)
  * Mātrā-vṛtta (matra-based meters like Āryā, Gīti)

* **Smart Identification**:

  * Exact pattern matching
  * Fuzzy matching with syllable-level correction suggestions
  * Verse-level analysis (4-line grouping)

* **Multi-Script Support**: 15+ scripts and transliteration schemes

  * Devanagari, IAST, ITRANS, Harvard-Kyoto, SLP1, WX, Velthuis, and more

* **Detailed Analysis**:

  * Syllable segmentation
  * Laghu-Guru (light-heavy) marking
  * Gana notation conversion
  * Mātrā (morae) counting
  * Jāti (classification) identification

Installation
------------

Install from PyPI:

.. code-block:: bash

   pip install chanda

Or from source:

.. code-block:: bash

   git clone https://github.com/hrishikeshrt/chanda.git
   cd chanda
   pip install -e .

Quick Start
-----------

Python API
~~~~~~~~~~

.. code-block:: python

   from chanda import identify_meter

   # Identify meter from a single line
   text = "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"
   result = identify_meter(text)

   print(result['display_chanda'])  # Output: Anuṣṭup (पाद 1)
   print(result['display_gana'])    # Output: नभजलगलग
   print(result['matra'])           # Output: 32

Command-Line Interface
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Analyze a single line
   chanda "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"

   # Analyze a file
   chanda -f bhagavad_gita.txt --verse --summary

   # Interactive mode
   chanda -i

   # Get help
   chanda --help

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   usage
   api

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/chanda
   api/core
   api/utils
   api/cli

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
