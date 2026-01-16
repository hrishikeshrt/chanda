Usage Guide
===========

Basic Usage
-----------

Single Line Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from chanda import analyze_line

   text = "रामो राजमणिः सदा विजयते रामं रमेशं भजे"
   result = analyze_line(text, fuzzy=True)

   if result.found:
       print(f"Meter(s): {[name for name, _ in result.chanda]}")
       print(f"Syllables: {result.syllables}")
       print(f"Pattern (LG): {' '.join(result.lg)}")
       print(f"Gana: {result.gana}")
       print(f"Syllable count: {result.length}")
       print(f"Mātrā count: {result.matra}")
   else:
       # Check fuzzy matches
       if result.fuzzy:
           best_match = result.fuzzy[0]
           from chanda import format_chanda_list
           print(f"Closest meter: {format_chanda_list(best_match['chanda'])}")
           print(f"Similarity: {best_match['similarity']:.2%}")

Verse Analysis
~~~~~~~~~~~~~~

.. code-block:: python

   from chanda import analyze_text

   verse = """को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्।
   धर्मज्ञश्च कृतज्ञश्च सत्यवाक्यो दृढव्रतः॥"""

   results = analyze_text(verse, verse_mode=True, fuzzy=True)

   # Access verse-level results
   for verse in results.result.verse:
       best_meters, score = verse.chanda
       print(f"Verse meter: {' / '.join(best_meters)} (score: {score})")

Command-Line Interface
----------------------

Basic Commands
~~~~~~~~~~~~~~

Analyze a single line:

.. code-block:: bash

   chanda "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"

Analyze a file:

.. code-block:: bash

   chanda -f input.txt

Enable fuzzy matching:

.. code-block:: bash

   chanda -f input.txt --fuzzy

Verse mode (group by 4 lines):

.. code-block:: bash

   chanda -f input.txt --verse

Show summary statistics:

.. code-block:: bash

   chanda -f input.txt --verse --summary

Interactive mode:

.. code-block:: bash

   chanda -i

Advanced Options
~~~~~~~~~~~~~~~~

Save results to file:

.. code-block:: bash

   chanda -f input.txt --verse --save-path ./results/

Specify input encoding:

.. code-block:: bash

   chanda -f input.txt --encoding utf-8

Get help:

.. code-block:: bash

   chanda --help

Working with Different Scripts
-------------------------------

Chanda automatically detects and supports multiple transliteration schemes:

.. code-block:: python

   from chanda import analyze_line

   # Devanagari
   result = analyze_line("धर्मक्षेत्रे कुरुक्षेत्रे")

   # IAST
   result = analyze_line("dharmakṣetre kurukṣetre")

   # ITRANS
   result = analyze_line("dharmakShetre kurukShetre")

   # Harvard-Kyoto
   result = analyze_line("dharmakSetre kurukSetre")

   # SLP1
   result = analyze_line("Darmakzetre kurukzetre")

Supported Meters
----------------

Sama-vṛtta (348 meters)
~~~~~~~~~~~~~~~~~~~~~~~

Meters with identical padas:

* Anuṣṭup
* Indravajrā
* Upendravajrā
* Vasantatilakā
* Mālinī
* Śārdūlavikrīḍita
* And 340+ more

Ardhasama-vṛtta
~~~~~~~~~~~~~~~~

Meters with alternating padas:

* Aparavaktra
* Upacitra
* And more

Viṣama-vṛtta
~~~~~~~~~~~~

Meters with uneven padas:

* Viyoginī
* And more

Mātrā-vṛtta (10 meters)
~~~~~~~~~~~~~~~~~~~~~~~~

Matra-based meters:

* Āryā
* Āryāgīti
* Udgīti
* Upagīti
* Gīti
* And 5+ more

Examples
--------

Example 1: Identify Anuṣṭup
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from chanda import analyze_line

   line = "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"
   result = analyze_line(line)

   print([name for name, _ in result.chanda])  # ['अनुष्टुभ्']
   print(result.gana)    # नभजलगलग

Example 2: Fuzzy Matching
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from chanda import analyze_line

   # Slightly incorrect meter
   line = "रामं राजमणिः सदा विजयते"
   result = analyze_line(line, fuzzy=True, k=5)

   if not result.found and result.fuzzy:
       for match in result.fuzzy[:3]:
           from chanda import format_chanda_list
           print(f"{format_chanda_list(match['chanda'])}: {match['similarity']:.1%}")
           print(f"  Suggestion: {match['suggestion']}")

Example 3: Batch Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from chanda import analyze_text

   with open('bhagavad_gita.txt', 'r', encoding='utf-8') as f:
       text = f.read()

   results = analyze_text(text, verse_mode=True, fuzzy=True)

   # Get summary statistics
   from chanda import Chanda
   from chanda.utils import get_default_data_path

   c = Chanda(get_default_data_path())
   summary = c.summarize_results(results.result.to_dict())
   print(c.format_summary(summary))
