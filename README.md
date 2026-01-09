# Chanda

[![PyPI version](https://badge.fury.io/py/chanda.svg)](https://badge.fury.io/py/chanda)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
from chanda import identify_meter

# Identify meter from a single line
text = "इक्ष्वाकुवंशप्रभवो रामो नाम जनैः श्रुतः"
result = identify_meter(text)

print(result['display_chanda'])  # Output: Anuṣṭup (पाद 1)
print(result['display_gana'])    # Output: नभजलगलग
print(result['matra'])           # Output: 32
```

### Command-Line Interface

```bash
# Analyze a single line
chanda "इक्ष्वाकुवंशप्रभवो रामो नाम जनैः श्रुतः"

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
from chanda import identify_meter

text = "रामो राजमणिः सदा विजयते रामं रमेशं भजे"
result = identify_meter(text, fuzzy=True)

if result['found']:
    print(f"Meter: {result['display_chanda']}")
    print(f"Syllables: {result['syllables']}")
    print(f"Pattern (LG): {' '.join(result['lg'])}")
    print(f"Gana: {result['gana']}")
    print(f"Syllable count: {result['length']}")
    print(f"Mātrā count: {result['matra']}")
else:
    # Check fuzzy matches
    if result['fuzzy']:
        best_match = result['fuzzy'][0]
        print(f"Closest meter: {best_match['display_chanda']}")
        print(f"Similarity: {best_match['similarity']:.2%}")
```

### Verse Analysis

```python
from chanda import analyze_text

verse = """इक्ष्वाकुवंशप्रभवो रामो नाम जनैः श्रुतः।
मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय॥"""

results = analyze_text(verse, verse_mode=True, fuzzy=True)

# Access verse-level results
for verse in results['result']['verse']:
    best_meters, score = verse['chanda']
    print(f"Verse meter: {' / '.join(best_meters)} (score: {score})")
```

---

## Documentation

Full documentation is available at [chanda.readthedocs.io](https://chanda.readthedocs.io)

---

## Project Structure

```
chanda/
├── chanda/               # Main package
│   ├── __init__.py       # Public API
│   ├── core.py           # Core Chanda class
│   ├── utils.py          # Utility functions
│   ├── cli.py            # Command-line interface
│   ├── exceptions.py     # Custom exceptions
│   └── data/             # Meter definitions (CSV files)
├── examples/             # Usage examples
├── docs/                 # Sphinx documentation
├── pyproject.toml        # Package configuration
├── setup.py              # Setup script
├── Makefile              # Build and test automation
└── README.md             # This file
```

---

## Supported Meters

### Sama-vṛtta (348 meters)
Anuṣṭup, Indravajrā, Upendravajrā, Vasantatilakā, Mālinī, Śārdūlavikrīḍita, and 340+ more

### Ardhasama/Viṣama-vṛtta (52 meters)
Aparavaktra, Upacitra, Viyoginī, and 49+ more

### Mātrā-vṛtta (10 meters)
Āryā, Āryāgīti, Udgīti, Upagīti, Gīti, and 5+ more

---

## Web Interface

A web interface built with Flask is available separately at:
https://github.com/hrishikeshrt/chanda

Live demo: https://sanskrit.iitk.ac.in/jnanasangraha/chanda/

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

If you use Chanda in your research, please cite:

```bibtex
@software{chanda2025,
  title = {Chanda: Sanskrit Meter Identification Library},
  author = {Terdalkar, Hrishikesh},
  year = {2025},
  url = {https://github.com/hrishikeshrt/chanda}
}
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

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
