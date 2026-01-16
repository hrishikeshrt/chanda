#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text processing utilities for Chandojñānam.

This module provides helpers for normalizing input text, detecting
transliteration schemes, and returning cleaned Devanagari lines.
"""

import functools
from typing import Tuple, List

import sanskrit_text as skt
from indic_transliteration import sanscript
from indic_transliteration.detect import detect
from indic_transliteration.sanscript import transliterate

from .constants import MAX_CACHE


class SanskritTextProcessor:
    """
    Helper class for Sanskrit text processing operations.

    Notes
    -----
    This class only contains static helpers and does not keep state.
    """

    @staticmethod
    @functools.lru_cache(maxsize=MAX_CACHE)
    def process_and_detect_scheme(text: str) -> Tuple[List[str], str]:
        """
        Process input text and detect transliteration scheme.

        Parameters
        ----------
        text : str
            Input Sanskrit text in any supported scheme.

        Returns
        -------
        list[str]
            Cleaned Devanagari lines (empty lines removed).
        str
            Detected transliteration scheme for the original input.
        """
        scheme = detect(text)
        if scheme != sanscript.DEVANAGARI:
            devanagari_text = transliterate(text, scheme, sanscript.DEVANAGARI)
        else:
            devanagari_text = text

        lines = []
        for line in skt.split_lines(devanagari_text):
            clean_line = skt.clean(line).strip()
            if clean_line:
                lines.append(clean_line)
        return lines, scheme
