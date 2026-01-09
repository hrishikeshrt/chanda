"""
Chandojñānam: Sanskrit Meter Identification Library
===================================================

A comprehensive Python library for identifying and analyzing Sanskrit poetic meters (chanda/छन्द).

Basic Usage:
    >>> from chanda import identify_meter
    >>> result = identify_meter("को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्")
    >>> print(result['display_chanda'])
    'Anuṣṭup'

Main Components:
    - Chanda: Core meter identification and analysis class
    - identify_meter: Convenient function for quick meter identification
    - analyze_text: Multi-line and verse analysis

Supported Features:
    - 200+ Sanskrit meters (Sama, Ardhasama, Vishama, Matra-based)
    - Exact and fuzzy pattern matching
    - Multi-script support (15+ schemes: Devanagari, IAST, ITRANS, etc.)
    - Syllable-level scansion (Laghu-Guru marking)
    - Gana notation conversion
    - Verse-level analysis
    - Matra (morae) counting for matra-based meters

Author: Hrishikesh Terdalkar
License: AGPL-3.0-or-later
"""

__version__ = "0.1.1"
__author__ = "Hrishikesh Terdalkar"

from .core import Chanda
from .utils import identify_meter, analyze_text, format_result
from .exceptions import ChandaError, InvalidInputError, MeterNotFoundError

__all__ = [
    'Chanda',
    'identify_meter',
    'analyze_text',
    'format_result',
    'ChandaError',
    'InvalidInputError',
    'MeterNotFoundError',
]
