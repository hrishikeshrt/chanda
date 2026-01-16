#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prosody analysis module - language-specific syllable weight marking.

This module provides an abstract base class for prosodic analysis and
language-specific implementations for marking syllable weights (laghu/guru).
"""

###############################################################################

import functools
from abc import ABC, abstractmethod
from typing import List, Tuple, Union

import sanskrit_text as skt

from .constants import MAX_CACHE, SyllableWeight, Language

###############################################################################


Syllables = List[List[List[str]]]


class ChandaAnalyzer(ABC):
    """
    Abstract base class for language-specific chanda (meter) analysis.

    Notes
    -----
    Each language implementation should implement ``mark_syllable_weights``
    according to its prosodic rules.
    """

    @abstractmethod
    def mark_syllable_weights(self, text: str) -> Tuple[Syllables, List[str]]:
        """
        Mark syllable weights (laghu/guru) for the given text.

        Parameters
        ----------
        text : str
            Input text in the target language.

        Returns
        -------
        list
            Nested syllable structure returned by the tokenizer.
        list[str]
            Weight marks, using ``'L'`` (laghu), ``'G'`` (guru), or ``''``.
        """
        pass

    @staticmethod
    def _is_empty_mark(syllable: str, skip_syllables: List[str]) -> bool:
        """
        Check if a syllable should have an empty weight mark.

        Parameters
        ----------
        syllable : str
            Input syllable to inspect.
        skip_syllables : list[str]
            Syllables that should be skipped or yield empty marks.

        Returns
        -------
        bool
            ``True`` if the syllable yields an empty mark.
        """
        return syllable in skip_syllables or syllable.endswith(skt.HALANTA)


class SanskritChandaAnalyzer(ChandaAnalyzer):
    """
    Sanskrit-specific chanda analyzer implementing traditional rules.

    Notes
    -----
    Laghu (light)
        Short vowel followed by a single consonant.
    Guru (heavy)
        Long vowel; short vowel followed by conjunct consonant; short vowel
        followed by anusvāra or visarga; or any vowel at line end.
    """

    @functools.lru_cache(maxsize=MAX_CACHE)
    def mark_syllable_weights(self, text: str) -> Tuple[Syllables, List[str]]:
        """
        Mark syllable weights according to Sanskrit prosodic rules.

        Parameters
        ----------
        text : str
            Sanskrit text in Devanagari.

        Returns
        -------
        list
            Nested syllable structure for the input.
        list[str]
            Laghu-guru marks aligned with flattened syllables.
        """
        skip_syllables = [skt.AVAGRAHA]
        lg_marks = []
        syllables = skt.get_syllables(text)
        flat_syllables = [s for ln in syllables for w in ln for s in w]

        if not flat_syllables:
            return flat_syllables, lg_marks

        # Process all syllables except the last
        for idx, syllable in enumerate(flat_syllables[:-1]):
            if self._is_empty_mark(syllable, skip_syllables):
                lg_marks.append('')
                continue

            # Check if laghu: short vowel + no following conjunct
            is_laghu = (
                skt.is_laghu(syllable) and
                (skt.HALANTA not in flat_syllables[idx + 1])
            )
            lg_marks.append(SyllableWeight.L.value if is_laghu else SyllableWeight.G.value)

        # Handle the last syllable (always guru by convention in verse final position)
        last_syllable = flat_syllables[-1]
        if self._is_empty_mark(last_syllable, skip_syllables):
            lg_marks.append('')
        else:
            # Last syllable can be laghu in pada-internal analysis
            is_laghu = skt.is_laghu(last_syllable)
            lg_marks.append(SyllableWeight.L.value if is_laghu else SyllableWeight.G.value)

        return syllables, lg_marks


class VedicChandaAnalyzer(SanskritChandaAnalyzer):
    """
    Vedic Sanskrit chanda analyzer.

    Notes
    -----
    Inherits from Sanskrit but can override rules specific to Vedic meters
    (e.g., treatment of pluta vowels, special sandhi rules).
    """

    def mark_syllable_weights(self, text: str) -> Tuple[Syllables, List[str]]:
        """
        Mark syllable weights according to Vedic prosodic rules.

        Parameters
        ----------
        text : str
            Vedic Sanskrit text in Devanagari.

        Returns
        -------
        list
            Nested syllable structure for the input.
        list[str]
            Laghu-guru marks aligned with flattened syllables.

        Notes
        -----
        Currently uses Classical Sanskrit rules as base.
        """
        # TODO: Add Vedic-specific rules
        # - Pluta vowels (three mātrās)
        # - Specific sandhi treatments
        # - Accent-based modifications
        return super().mark_syllable_weights(text)


class PrakritChandaAnalyzer(ChandaAnalyzer):
    """
    Prakrit chanda analyzer.

    Notes
    -----
    Similar to Sanskrit but with variations in treatment of consonant clusters
    and simplified pronunciation.
    """

    @functools.lru_cache(maxsize=MAX_CACHE)
    def mark_syllable_weights(self, text: str) -> Tuple[Syllables, List[str]]:
        """
        Mark syllable weights according to Prakrit prosodic rules.

        Parameters
        ----------
        text : str
            Prakrit text in Devanagari.

        Returns
        -------
        list
            Nested syllable structure for the input.
        list[str]
            Laghu-guru marks aligned with flattened syllables.
        """
        # TODO: Implement Prakrit-specific rules
        # For now, use Sanskrit as base with modifications
        skip_syllables = [skt.AVAGRAHA]
        lg_marks = []
        syllables = skt.get_syllables(text)
        flat_syllables = [s for ln in syllables for w in ln for s in w]

        if not flat_syllables:
            return flat_syllables, lg_marks

        for idx, syllable in enumerate(flat_syllables[:-1]):
            if self._is_empty_mark(syllable, skip_syllables):
                lg_marks.append('')
                continue

            is_laghu = (
                skt.is_laghu(syllable) and
                (skt.HALANTA not in flat_syllables[idx + 1])
            )
            lg_marks.append(SyllableWeight.L.value if is_laghu else SyllableWeight.G.value)

        # Last syllable
        last_syllable = flat_syllables[-1]
        if self._is_empty_mark(last_syllable, skip_syllables):
            lg_marks.append('')
        else:
            is_laghu = skt.is_laghu(last_syllable)
            lg_marks.append(SyllableWeight.L.value if is_laghu else SyllableWeight.G.value)

        return syllables, lg_marks


# Factory function to get appropriate analyzer
def get_chanda_analyzer(language: Union[str, Language] = Language.SANSKRIT) -> ChandaAnalyzer:
    """
    Factory function to get language-specific chanda analyzer.

    Parameters
    ----------
    language : str or Language, optional
        Language code (``Language`` enum or string: ``'sanskrit'``,
        ``'vedic'``, ``'prakrit'``).

    Returns
    -------
    ChandaAnalyzer
        Language-specific analyzer instance.

    Raises
    ------
    ValueError
        If the language is not supported.

    Examples
    --------
    >>> from chanda.constants import Language
    >>> analyzer = get_chanda_analyzer(Language.SANSKRIT)
    >>> analyzer = get_chanda_analyzer('sanskrit')
    """
    analyzers = {
        Language.SANSKRIT.value: SanskritChandaAnalyzer,
        Language.VEDIC.value: VedicChandaAnalyzer,
        Language.PRAKRIT.value: PrakritChandaAnalyzer,
    }

    # Convert enum to string if needed
    lang_str = language.value if isinstance(language, Language) else language.lower()

    analyzer_class = analyzers.get(lang_str)
    if not analyzer_class:
        supported = ', '.join(analyzers.keys())
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Supported languages: {supported}"
        )

    return analyzer_class()


###############################################################################
