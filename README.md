# Chanda

[![PyPI version](https://badge.fury.io/py/chanda.svg)](https://badge.fury.io/py/chanda)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

**Sanskrit Meter Identification and Analysis Library**

A comprehensive Python library for identifying and analyzing Sanskrit poetic meters. Supports 200+ meters including Sama-vṛtta, Ardhasama-vṛtta, Viṣama-vṛtta, and Mātrā-vṛtta.

* Chandojñānam Web Interface: [https://sanskrit.iitk.ac.in/jnanasangraha/chanda/](https://sanskrit.iitk.ac.in/jnanasangraha/chanda/)
* Chandojñānam Web Interface Source Code: [https://github.com/hrishikeshrt/chandojnanam/](https://github.com/hrishikeshrt/chandojnanam/)

---

## Features

- **200+ Meter Database**: Comprehensive coverage of Sanskrit meters
  - Sama-vṛtta (meters with identical padas)
  - Ardhasama-vṛtta & Viṣama-vṛtta (meters with varying padas)
  - Mātrā-vṛtta (matra-based meters like Āryā, Gīti)

- **Smart Identification**:
  - Exact pattern matching
  - Fuzzy matching with syllable-level correction suggestions
  - Verse-level analysis (4-line grouping)

- **Multi-Script Support**: 15+ scripts and transliteration schemes
  - Devanagari, IAST, ITRANS, Harvard-Kyoto, SLP1, WX, Velthuis, and more

- **Detailed Analysis**:
  - Syllable segmentation
  - Laghu-Guru (light-heavy) marking
  - Gana notation conversion
  - Mātrā (morae) counting
  - Jāti (classification) identification

---

## Installation

### From PyPI

```bash
pip install chanda
```

### From Source

```bash
git clone https://github.com/hrishikeshrt/chanda.git
cd chanda
pip install -e .
```

---

## Quick Start

### Python API

```python
from chanda import analyze_line

# Simple example - Anuṣṭubh (most common meter)
text = "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"
result = analyze_line(text)
meters = [name for name, _ in result.chanda]
print(meters)  # Output: ['अनुष्टुभ्']

# Gana-based meter example - shows gana pattern
text = "नमस्ते सदा वत्सले मातृभूमे"
result = analyze_line(text)
meters = [name for name, _ in result.chanda]
print(meters)  # Output: ['भुजङ्गप्रयात']
print(result.gana)            # Output: यययय
```

Results are objects (`ChandaResult` / `TextAnalysisResult`).
Use `result.to_dict()` or `result.to_json()` for serialization.

### Command-Line Interface

```bash
# Analyze a single line
chanda "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"

# Analyze a file
chanda -f bhagavad_gita.txt --verse --summary

# Interactive mode
chanda -i

# Get help
chanda --help
```

---

## Detailed Usage

### Single Line Analysis

```python
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
```

### Verse Analysis

```python
from chanda import analyze_text

verse = """को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्।
धर्मज्ञश्च कृतज्ञश्च सत्यवाक्यो दृढव्रतः॥"""

results = analyze_text(verse, verse_mode=True, fuzzy=True)

# Access verse-level results
for verse in results.result.verse:
    if not verse.chanda:
        continue
    best_meters, score = verse.chanda
    print(f"Verse meter: {' / '.join(best_meters)} (score: {score})")
```

---

## Documentation

Full documentation is available at [chanda.readthedocs.io](https://chanda.readthedocs.io)

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite
5. Submit a pull request

---

## Citation

If you use Chandojñānam in your research, please cite:

```bibtex
@inproceedings{terdalkar2023chandojnanam,
    title = "Chandojnanam: A {S}anskrit Meter Identification and Utilization System",
    author = "Terdalkar, Hrishikesh  and
      Bhattacharya, Arnab",
    booktitle = "Proceedings of the Computational {S}anskrit {\&} Digital Humanities: Selected papers presented at the 18th World {S}anskrit Conference",
    month = jan,
    year = "2023",
    address = "Canberra, Australia (Online mode)",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.wsc-csdh.8",
    pages = "113--127",
}
```

---

## License

GNU Affero General Public License v3.0 - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Based on traditional chandaśāstra texts
- Meter definitions compiled from various classical sources
- Built on the excellent `sanskrit-text` and `indic-transliteration` libraries

---

## Links

- **PyPI**: https://pypi.org/project/chanda/
- **GitHub**: https://github.com/hrishikeshrt/chanda
- **Documentation**: https://chanda.readthedocs.io
- **Issues**: https://github.com/hrishikeshrt/chanda/issues
