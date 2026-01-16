#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Display formatting helpers for Chandojñānam results.

This module provides utilities to turn structured results into
human-readable strings suitable for CLI or logs.
"""

from typing import Any, List, Tuple


def _as_dict(value: Any) -> Any:
    """
    Normalize result-like objects into a dictionary.

    Parameters
    ----------
    value : object
        Result-like object with ``to_dict`` or a raw dictionary.

    Returns
    -------
    object
        Dictionary representation if available; otherwise the original value.
    """
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def format_chanda_pada(chanda: str, pada: tuple) -> str:
    """
    Format a meter name with its pada annotation.

    Parameters
    ----------
    chanda : str
        Meter name.
    pada : tuple
        Tuple describing the pada positions for the meter.

    Returns
    -------
    str
        Human-readable meter name with pada information.

    Raises
    ------
    ValueError
        If the length of ``pada`` is not supported.
    """
    if not pada:
        return chanda
    if len(pada) == 1:
        return f"{chanda} (पाद {pada[0]})" if pada[0] else chanda
    if len(pada) == 2:
        return f"{chanda} (पाद {pada[0]}-{pada[1]})"
    if len(pada) == 4:
        return f"{chanda} (पाद {pada[0]}-{pada[3]})"
    raise ValueError("Invalid pada length")


def format_chanda_list(chanda_list: List[Tuple[str, Tuple]]) -> str:
    """
    Format a list of (meter, pada) tuples into a display string.

    Parameters
    ----------
    chanda_list : list[tuple[str, tuple]]
        List of meter names and their pada annotations.

    Returns
    -------
    str
        Formatted meter list joined with separators.
    """
    return ' / '.join(format_chanda_pada(c, p) for c, p in chanda_list)


def format_line_result(line_result) -> str:
    """
    Format a line-level identification result.

    Parameters
    ----------
    line_result : object
        ``ChandaResult``/``LineResult`` or dict representation.

    Returns
    -------
    str
        Multi-line formatted string describing the result.
    """
    line_result = _as_dict(line_result)
    if isinstance(line_result, dict) and 'result' in line_result and 'found' not in line_result:
        line_result = line_result['result']

    def _join(values: List[str], sep: str) -> str:
        if not values:
            return ""
        if isinstance(values, str):
            return values
        return sep.join(str(v) for v in values if v)

    syllables = _join(line_result.get('syllables', []), " | ")
    lg = _join(line_result.get('lg', []), " ")
    gana = line_result.get('gana', "")
    length = line_result.get('length', 0)
    matra = line_result.get('matra', 0)
    chanda_list = line_result.get('chanda', [])
    jaati_list = line_result.get('jaati', [])
    display_chanda = (
        format_chanda_list(chanda_list)
        if chanda_list else "Not found"
    )
    display_jaati = (
        _join(jaati_list, " / ")
        if jaati_list else "Unknown"
    )

    output_lines = [
        line_result.get('line', ''),
        f"  Syllables: {syllables or '[]'}",
        f"  LG: {lg or '[]'}",
        f"  Ga\u1e47a: {gana}",
        f"  Counts: {length} syllables, {matra} morae",
        f"  Chanda: {display_chanda}",
        f"  J\u0101ti: {display_jaati}",
    ]
    if line_result.get('fuzzy'):
        best_match = line_result['fuzzy'][0]
        similarity = best_match.get('similarity')
        similarity_str = (
            f"{similarity:.2%}" if isinstance(similarity, float) else str(similarity)
        )
        fuzzy_chanda = (
            format_chanda_list(best_match.get('chanda', []))
            if best_match.get('chanda') else "Not found"
        )
        output_lines.extend([
            f"  Fuzzy: {fuzzy_chanda} ({similarity_str})",
            f"    {best_match['suggestion']}"
        ])
    return "\n".join(output_lines)


def format_summary(result_summary) -> str:
    """
    Format aggregate summary statistics.

    Parameters
    ----------
    result_summary : dict
        Summary payload from ``Chanda.summarize_results``.

    Returns
    -------
    str
        Human-readable summary report.
    """
    output = []
    if result_summary["verse"]:
        output.extend([
            "Verse Statistics",
            "----------------"
        ])
        for idx, (chanda_name, chanda_count) in enumerate(
            result_summary["verse"]["chanda"].most_common(),
            start=1
        ):
            output.append(f"{idx:>4}. {chanda_name}: {chanda_count}")
        output.append("")

    output.extend([
        "Line Statistics",
        "---------------"
    ])

    if result_summary["line"]["match"]:
        output.append("-- Exact Match")
        for idx, (chanda_name, chanda_count) in enumerate(
            result_summary["line"]["match"]["chanda"].most_common(),
            start=1
        ):
            output.append(f"{idx:>4}. {chanda_name}: {chanda_count}")
        output.append("")

    if result_summary["line"]["fuzzy"]:
        output.append("-- Fuzzy Match")
        for idx, (chanda_name, chanda_count) in enumerate(
            result_summary["line"]["fuzzy"]["chanda"].most_common(),
            start=1
        ):
            output.append(f"{idx:>4}. {chanda_name}: {chanda_count}")
        output.append("")

    counts = result_summary["count"]
    output.extend([
        "Counts",
        "------",
        f"* Total Lines: {counts['line']}",
        f"  - Exact Match: {counts['match_line']}",
        f"  - Fuzzy Match: {counts['fuzzy_line']}",
        f"* Total Verses: {counts['verse']}",
        f"  - Exact Match: {counts['match_verse']}",
        f"  - Fuzzy Match: {counts['fuzzy_verse']}",
        f"* Total Syllables Mismatched: {counts['mismatch_syllable']}",
    ])

    return "\n".join(output)
