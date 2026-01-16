#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Type definitions for Chanda results.

This module provides dataclasses for structured result objects used across
the library and public API.
"""

import json

from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Optional, Dict, Any, Union

###############################################################################
# Data Classes for Result Types


@dataclass
class ChandaResult:
    """
    Result of meter identification for a single line.

    Attributes
    ----------
    line : str
        Line text in the selected output scheme.
    scheme : str or None
        Output scheme used for line rendering.
    found : bool
        Whether an exact meter match was found.
    syllables : list[str]
        List of syllables in the text.
    lg : list[str]
        Laghu-guru pattern (list of ``'L'`` or ``'G'``).
    gana : str
        Gaṇa notation string.
    length : int
        Total syllable count.
    matra : int
        Total mātrā count.
    chanda : list[tuple[str, tuple]]
        Matching meters as ``(meter_name, pada)`` tuples.
    jaati : list[str]
        Jāti classification labels.
    fuzzy : list[dict]
        Fuzzy match results (if no exact match found).
    """
    line: str = ""
    scheme: Optional[str] = None
    found: bool = False
    syllables: List[str] = field(default_factory=list)
    lg: List[str] = field(default_factory=list)
    gana: str = ""
    length: int = 0
    matra: int = 0
    chanda: List[Tuple[str, Tuple]] = field(default_factory=list)
    jaati: List[str] = field(default_factory=list)
    fuzzy: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the result.
        """
        return asdict(self)

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        """
        Serialize result to JSON.

        Parameters
        ----------
        indent : int, optional
            JSON indentation level.
        ensure_ascii : bool, optional
            Whether to escape non-ASCII characters.

        Returns
        -------
        str
            JSON string representation.
        """
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChandaResult':
        """
        Create a result from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary payload.

        Returns
        -------
        ChandaResult
            Parsed result object.
        """
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


# --------------------------------------------------------------------------- #


@dataclass
class LineResult:
    """
    Result wrapper for a single input line.

    Attributes
    ----------
    result : ChandaResult
        Meter identification result for the line.
    index : int or None
        Line index in the input sequence.
    """
    result: ChandaResult
    index: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the line result.
        """
        result = self.result
        if isinstance(result, ChandaResult):
            result = result.to_dict()
        payload = {'result': result}
        if self.index is not None:
            payload['index'] = self.index
        return payload

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        """
        Serialize result to JSON.

        Parameters
        ----------
        indent : int, optional
            JSON indentation level.
        ensure_ascii : bool, optional
            Whether to escape non-ASCII characters.

        Returns
        -------
        str
            JSON string representation.
        """
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LineResult':
        """
        Create a LineResult from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary payload with ``result`` and optional ``index``.

        Returns
        -------
        LineResult
            Parsed result object.
        """
        result = data.get('result')
        if isinstance(result, dict):
            result = ChandaResult.from_dict(result)
        return cls(result=result, index=data.get('index'))


# --------------------------------------------------------------------------- #


@dataclass
class VerseResult:
    """
    Result of verse-level analysis.

    Attributes
    ----------
    chanda : tuple[list[str], float] or None
        Best-matching meters and score.
    scores : list[tuple[str, float]]
        All meter scores for the verse.
    line_indices : list[int]
        Line indices belonging to this verse.
    line_results : list[LineResult]
        Line-wise results for this verse.
    """
    chanda: Optional[Tuple[List[str], float]] = None
    scores: List[Tuple[str, float]] = field(default_factory=list)
    line_indices: List[int] = field(default_factory=list)
    line_results: List[LineResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the verse result.
        """
        return {
            'chanda': self.chanda,
            'scores': self.scores,
            'line_indices': list(self.line_indices),
            'line_results': [line.to_dict() for line in self.line_results],
        }

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        """
        Serialize result to JSON.

        Parameters
        ----------
        indent : int, optional
            JSON indentation level.
        ensure_ascii : bool, optional
            Whether to escape non-ASCII characters.

        Returns
        -------
        str
            JSON string representation.
        """
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerseResult':
        """
        Create a VerseResult from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary payload with verse details.

        Returns
        -------
        VerseResult
            Parsed result object.
        """
        line_results = [
            LineResult.from_dict(item) for item in data.get('line_results', [])
        ]
        return cls(
            chanda=data.get('chanda'),
            scores=data.get('scores', []),
            line_indices=data.get('line_indices', data.get('lines', [])),
            line_results=line_results
        )


# --------------------------------------------------------------------------- #


@dataclass
class AnalysisResult:
    """
    Result of analyzing multi-line text.

    Attributes
    ----------
    scheme : str or None
        Output scheme used for line rendering.
    line : list[LineResult]
        Per-line identification results.
    verse : list[VerseResult]
        Verse-level aggregation results.
    """
    scheme: Optional[str] = None
    line: List[LineResult] = field(default_factory=list)
    verse: List[VerseResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the analysis result.
        """
        return {
            'scheme': self.scheme,
            'line': [line.to_dict() for line in self.line],
            'verse': [verse.to_dict() for verse in self.verse]
        }

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        """
        Serialize result to JSON.

        Parameters
        ----------
        indent : int, optional
            JSON indentation level.
        ensure_ascii : bool, optional
            Whether to escape non-ASCII characters.

        Returns
        -------
        str
            JSON string representation.
        """
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """
        Create an AnalysisResult from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary payload with ``line`` and ``verse`` fields.

        Returns
        -------
        AnalysisResult
            Parsed result object.
        """
        line_results = [LineResult.from_dict(item) for item in data.get('line', [])]
        verse_results = [VerseResult.from_dict(item) for item in data.get('verse', [])]
        return cls(
            scheme=data.get('scheme'),
            line=line_results,
            verse=verse_results
        )


# --------------------------------------------------------------------------- #


@dataclass
class MeterStats:
    """
    Statistics about supported meters in the database.

    Attributes
    ----------
    total : int
        Total number of unique meters.
    sama : int
        Number of Sama-vṛtta meters.
    ardhasama : int
        Number of Ardhasama-vṛtta meters.
    vishama : int
        Number of Viṣama-vṛtta meters.
    matra : int
        Number of Mātrā-vṛtta meters.
    """
    total: int
    sama: int
    ardhasama: int
    vishama: int
    matra: int

    def to_dict(self) -> Dict[str, int]:
        """
        Convert stats to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of meter statistics.
        """
        return asdict(self)

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        """
        Serialize stats to JSON.

        Parameters
        ----------
        indent : int, optional
            JSON indentation level.
        ensure_ascii : bool, optional
            Whether to escape non-ASCII characters.

        Returns
        -------
        str
            JSON string representation.
        """
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'MeterStats':
        """
        Create MeterStats from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary payload.

        Returns
        -------
        MeterStats
            Parsed stats object.
        """
        return cls(**data)


# --------------------------------------------------------------------------- #


@dataclass
class TextAnalysisResult:
    """
    Result of analyzing multi-line text.

    Attributes
    ----------
    result : AnalysisResult or dict
        Analysis payload with ``line`` and ``verse`` results.
    path : dict
        File paths for saved results (if any).
    """
    result: Union[AnalysisResult, Dict[str, Any]]
    path: Dict[str, Optional[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to a dictionary.

        Returns
        -------
        dict
            Dictionary representation with ``result`` and ``path``.
        """
        result = self.result
        if isinstance(result, AnalysisResult):
            result = result.to_dict()
        return {
            'result': result,
            'path': self.path
        }

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        """
        Serialize result to JSON.

        Parameters
        ----------
        indent : int, optional
            JSON indentation level.
        ensure_ascii : bool, optional
            Whether to escape non-ASCII characters.

        Returns
        -------
        str
            JSON string representation.
        """
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextAnalysisResult':
        """
        Create a TextAnalysisResult from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary payload with ``result`` and ``path``.

        Returns
        -------
        TextAnalysisResult
            Parsed result object.
        """
        result = data.get('result')
        if isinstance(result, dict):
            result = AnalysisResult.from_dict(result)
        return cls(result=result, path=data.get('path', {}))


###############################################################################
