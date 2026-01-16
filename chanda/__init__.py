"""
Chandojñānam: Sanskrit Meter Identification Library.

Extended Summary
----------------
A Python library for identifying and analyzing Sanskrit poetic meters
(chanda/छन्द), including Sama, Ardhasama, Viṣama, and Mātrā-vṛtta meters.

Notes
-----
Main components include:
- ``Chanda``: core meter identification and analysis class
- ``analyze_line``: quick meter identification for a single line
- ``analyze_text``: multi-line and verse analysis

Supported features include:
- 200+ Sanskrit meters
- Exact and fuzzy pattern matching
- Multi-script support (Devanagari, IAST, ITRANS, etc.)
- Syllable-level scansion (Laghu-Guru marking)
- Gaṇa notation conversion
- Verse-level analysis
- Mātrā counting for mātrā-based meters

Examples
--------
>>> from chanda import analyze_line
>>> result = analyze_line("को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्")
>>> print([name for name, _ in result.chanda])
['Anuṣṭup']
"""

__version__ = "1.0.0"
__author__ = "Hrishikesh Terdalkar"

from .core import Chanda, analyze_line, analyze_text
from .formatter import format_result, display_fields, format_chanda_list
from .utils import get_supported_meters
from .types import (
    ChandaResult,
    LineResult,
    VerseResult,
    AnalysisResult,
    MeterStats,
    TextAnalysisResult
)
from .constants import Language
from .exceptions import ChandaError, InvalidInputError, MeterNotFoundError

__all__ = [
    # Core classes and functions
    'Chanda',
    'analyze_line',
    'analyze_text',
    # Formatting
    'format_result',
    'display_fields',
    'format_chanda_list',
    # Utilities
    'get_supported_meters',
    # Types
    'ChandaResult',
    'LineResult',
    'VerseResult',
    'AnalysisResult',
    'MeterStats',
    'TextAnalysisResult',
    # Constants
    'Language',
    # Exceptions
    'ChandaError',
    'InvalidInputError',
    'MeterNotFoundError',
]
