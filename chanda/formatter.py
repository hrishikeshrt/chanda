#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formatting functions for Chanda results.

This module provides helpers to format meter identification results as
human-readable text for CLI or application output.
"""

from typing import Any, Dict, List, Tuple, Union
from .types import ChandaResult, LineResult, TextAnalysisResult, AnalysisResult


def _coerce_result(result: Union[ChandaResult, LineResult, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalize result-like inputs into a plain dictionary.

    Parameters
    ----------
    result : ChandaResult or LineResult or dict
        Result object or dictionary to normalize.

    Returns
    -------
    dict
        Dictionary representation with a single line result payload.
    """
    if isinstance(result, LineResult):
        result = result.result
    if isinstance(result, ChandaResult):
        result = result.to_dict()
    if isinstance(result, dict) and 'result' in result and 'found' not in result:
        result = result['result']
    return result


def format_result(result: Union[ChandaResult, LineResult, Dict[str, Any]]) -> str:
    """
    Format meter identification result as human-readable text.

    Parameters
    ----------
    result : ChandaResult or LineResult or dict
        Result from ``analyze_line`` or its dict form.

    Returns
    -------
    str
        Formatted multi-line string representation.

    Examples
    --------
    >>> result = analyze_line("को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्")
    >>> print(format_result(result))
    को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्
        Syllables: को | न्व | स्मिन् | सा | ...
        LG: ग ग ग ल ...
        Gana: मरतयजग
        ...
    """
    result = _coerce_result(result)

    from .display import format_line_result
    return format_line_result(result)


def format_chanda_list(chanda_list: List[Tuple[str, Tuple]]) -> str:
    """
    Format a list of (name, pada) tuples for display.

    Parameters
    ----------
    chanda_list : list[tuple[str, tuple]]
        Meter list with pada annotations.

    Returns
    -------
    str
        Display string joined with separators.
    """
    from .display import format_chanda_list as _format_chanda_list
    return _format_chanda_list(chanda_list)


def display_fields(result: Union[ChandaResult, LineResult, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build display-friendly fields from a result object or dict.

    Parameters
    ----------
    result : ChandaResult or LineResult or dict
        Result object or dictionary to format.

    Returns
    -------
    dict
        Payload with display_* fields.
    """
    result = _coerce_result(result)

    chanda_list = result.get('chanda', [])
    from .display import format_chanda_list as _format_chanda_list
    display_chanda = _format_chanda_list(chanda_list) if chanda_list else ''
    display_jaati = ' / '.join(result.get('jaati', [])) if result.get('jaati') else ''

    return {
        'display_line': result.get('line', ''),
        'display_syllables': result.get('syllables', []),
        'display_lg': result.get('lg', []),
        'display_gana': result.get('gana', ''),
        'display_length': result.get('length', 0),
        'display_matra': result.get('matra', 0),
        'display_chanda': display_chanda,
        'display_jaati': display_jaati,
    }


def format_verse_result(verse_result: Dict[str, Any]) -> str:
    """
    Format verse-level analysis result.

    Parameters
    ----------
    verse_result : dict
        Verse-level analysis result dictionary.

    Returns
    -------
    str
        Formatted string representation of verse analysis.
    """
    if hasattr(verse_result, "to_dict"):
        verse_result = verse_result.to_dict()

    output = []

    if 'chanda' in verse_result and verse_result['chanda']:
        meters, score = verse_result['chanda']
        output.append(f"Verse Meter: {' / '.join(meters)} (score: {score})")

    if 'line_indices' in verse_result:
        output.append(f"Lines: {', '.join(map(str, verse_result['line_indices']))}")

    if 'scores' in verse_result and verse_result['scores']:
        output.append(f"Top scores: {verse_result['scores'][:3]}")

    return '\n'.join(output)


def format_analysis_summary(results: Dict[str, Any]) -> str:
    """
    Format text analysis summary.

    Parameters
    ----------
    results : dict
        Results from ``analyze_text``.

    Returns
    -------
    str
        Formatted summary string.
    """
    # Import here to avoid circular dependency
    from .core import Chanda

    if isinstance(results, TextAnalysisResult):
        results = results.to_dict()
    if isinstance(results, AnalysisResult):
        results = {'result': results.to_dict()}
    if 'result' not in results:
        return "No results available"

    # Create a temporary Chanda instance to use its formatting
    # This is a bit hacky but maintains backward compatibility
    summary_data = {
        'line': results['result'].get('line', []),
        'verse': results['result'].get('verse', [])
    }

    # Use Chanda's summarize_results if available
    return f"Analysis complete: {len(summary_data['line'])} lines, {len(summary_data['verse'])} verses"
