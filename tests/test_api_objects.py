#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for object-oriented API results and formatting helpers.

Extended Summary
----------------
Validates object return types, JSON/dict serialization, formatting helpers,
and output scheme transliteration.
"""

import json
import re

from chanda import analyze_text, analyze_line, display_fields, format_chanda_list
from chanda.display import format_line_result
from chanda.processor import SanskritTextProcessor
from chanda.types import AnalysisResult, ChandaResult, LineResult, TextAnalysisResult, VerseResult


def test_analyze_line_returns_object():
    """
    Test analyze_line returns a ChandaResult object.
    """
    line = "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"
    result = analyze_line(line)

    assert isinstance(result, ChandaResult)
    payload = result.to_dict()
    assert isinstance(payload, dict)
    assert "found" in payload


def test_analyze_line_output_scheme():
    """
    Test output scheme transliteration in analyze_line.
    """
    line = "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"
    result = analyze_line(line, output_scheme="iast")

    assert result.scheme == "iast"
    assert not re.search(r"[\u0900-\u097F]", result.line)


def test_analyze_text_returns_objects():
    """
    Test analyze_text returns structured result objects.
    """
    verse = (
        "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्\n"
        "धर्मज्ञश्च कृतज्ञश्च सत्यवाक्यो दृढव्रतः॥"
    )
    results = analyze_text(verse, verse_mode=True, fuzzy=True)

    assert isinstance(results, TextAnalysisResult)
    assert isinstance(results.result, AnalysisResult)
    assert results.result.line
    assert all(isinstance(item, LineResult) for item in results.result.line)

    if results.result.verse:
        verse_result = results.result.verse[0]
        assert isinstance(verse_result, VerseResult)
        assert verse_result.line_results


def test_format_helpers():
    """
    Test formatting helpers on object results.
    """
    line = "नमस्ते सदा वत्सले मातृभूमे"
    result = analyze_line(line)

    formatted = format_line_result(result)
    assert isinstance(formatted, str)

    chanda_display = format_chanda_list(result.chanda)
    assert isinstance(chanda_display, str)

    display = display_fields(result)
    assert isinstance(display, dict)
    assert "display_line" in display


def test_to_json_serialization():
    """
    Test JSON serialization helpers on result objects.
    """
    line = "नमस्ते सदा वत्सले मातृभूमे"
    result = analyze_line(line)
    data = json.loads(result.to_json())

    assert isinstance(data, dict)
    assert "line" in data


def test_processor_scheme_detection():
    """
    Test scheme detection and line cleaning in the processor.
    """
    text = "dharmakṣetre kurukṣetre samavetā yuyutsavaḥ"
    lines, scheme = SanskritTextProcessor.process_and_detect_scheme(text)

    assert lines
    assert isinstance(scheme, str)
