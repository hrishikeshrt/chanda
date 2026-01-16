#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constants and enumerations for Sanskrit prosody.

This module defines the core constants, enums, and symbols used throughout
the Chandojñānam library.
"""

###############################################################################

from enum import Enum

###############################################################################

# Cache and configuration constants
MAX_CACHE = 8192  # Size of LRU cache for memoization
DEFAULT_VERSE_LINES = 4  # Number of lines per verse (śloka)

###############################################################################


class SyllableWeight(str, Enum):
    """
    Syllable weight in Sanskrit prosody.

    Attributes
    ----------
    L : str
        Laghu (light/short syllable, 1 mātrā).
    G : str
        Guru (heavy/long syllable, 2 mātrā).
    """
    L = 'L'  # Laghu (light)
    G = 'G'  # Guru (heavy)


class GanaSymbol(str, Enum):
    """
    Gaṇa symbols used in Sanskrit prosody.

    Notes
    -----
    Each gaṇa represents a three-syllable pattern of laghu and guru.
    The eight gaṇas are: ya, ra, ta, na, bha, ja, sa, ma.
    """
    Y = 'Y'  # ya-gaṇa: L-G-G (त्रिकलं द्विगुरु)
    R = 'R'  # ra-gaṇa: G-L-G (मध्ये लघु)
    T = 'T'  # ta-gaṇa: G-G-L (गुरुद्वयं लघु)
    N = 'N'  # na-gaṇa: L-L-L (त्रिलघु)
    B = 'B'  # bha-gaṇa: G-L-L (आदिगुरु)
    J = 'J'  # ja-gaṇa: L-G-L (मध्ये गुरु)
    S = 'S'  # sa-gaṇa: L-L-G (लघुद्वयं गुरु)
    M = 'M'  # ma-gaṇa: G-G-G (त्रिगुरु)


class Language(str, Enum):
    """
    Supported languages for prosody analysis.

    Attributes
    ----------
    SANSKRIT : str
        Classical Sanskrit rules.
    VEDIC : str
        Vedic Sanskrit rules.
    PRAKRIT : str
        Prakrit rules.
    """
    SANSKRIT = 'sanskrit'
    VEDIC = 'vedic'
    PRAKRIT = 'prakrit'
    # Future support
    # MARATHI = 'marathi'
    # HINDI = 'hindi'
    # BENGALI = 'bengali'
    # TELUGU = 'telugu'


###############################################################################
