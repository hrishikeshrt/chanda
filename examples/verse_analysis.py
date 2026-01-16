#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verse analysis examples for Chandojñānam library.

This script demonstrates analyzing complete verses and multi-line texts.
"""

from chanda import analyze_text
from chanda.core import Chanda
from chanda.utils import get_default_data_path

def example_1_bhagavad_gita_verse():
    """Example 1: Analyze a verse from Bhagavad Gītā."""
    print("="*80)
    print("Example 1: Bhagavad Gītā Verse")
    print("="*80)

    verse = """को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्।
धर्मज्ञश्च कृतज्ञश्च सत्यवाक्यो दृढव्रतः॥"""

    print("Input verse:")
    print(verse)
    print()

    results = analyze_text(verse, verse_mode=True, fuzzy=True)

    # Print verse-level result
    for verse_result in results.result.verse:
        best_meters, score = verse_result.chanda
        print(f"Identified meter: {' / '.join(best_meters)}")
        print(f"Confidence score: {score}/4")
        print()

    # Print line-by-line results
    print("Line-by-line analysis:")
    for i, line_result in enumerate(results.result.line, 1):
        result = line_result.result
        print(f"\nLine {i}: {result.line}")
        print(f"  Meter: {[name for name, _ in result.chanda]}")
        print(f"  Pattern: {result.gana}")
        print(f"  LG: {' '.join(result.lg)}")

    print()


def example_2_multiple_verses():
    """Example 2: Analyze multiple verses."""
    print("="*80)
    print("Example 2: Multiple Verses")
    print("="*80)

    text = """को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्।
धर्मज्ञश्च कृतज्ञश्च सत्यवाक्यो दृढव्रतः॥
दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा।
आचार्यमुपसङ्गम्य राजा वचनमब्रवीत्॥"""

    print("Input (2 verses, 4 lines):")
    print(text)
    print()

    results = analyze_text(text, verse_mode=True, fuzzy=True)

    print(f"Total verses analyzed: {len(results.result.verse)}")
    print()

    for i, verse_result in enumerate(results.result.verse, 1):
        best_meters, score = verse_result.chanda
        print(f"Verse {i}: {' / '.join(best_meters)} (score: {score})")

    print()


def example_3_line_mode():
    """Example 3: Line-by-line mode (no verse grouping)."""
    print("="*80)
    print("Example 3: Line-by-Line Mode")
    print("="*80)

    text = """वन्दे मातरम्
सुजलां सुफलां मलयजशीतलाम्
शस्यश्यामलां मातरम्"""

    print("Input:")
    print(text)
    print()

    results = analyze_text(text, verse_mode=False, fuzzy=True)

    print("Independent line analysis:")
    for i, line_result in enumerate(results.result.line, 1):
        result = line_result.result
        print(f"\nLine {i}: {result.line}")
        if result.found:
            print(f"  Meter: {[name for name, _ in result.chanda]}")
        else:
            print("  Meter: Not found (fuzzy matching enabled)")
            if result.fuzzy:
                from chanda import format_chanda_list
                top = result.fuzzy[0]
                print(f"  Closest: {format_chanda_list(top['chanda'])} ({top['similarity']:.1%})")

    print()


def example_4_statistics_summary():
    """Example 4: Get statistics summary for a text."""
    print("="*80)
    print("Example 4: Statistics Summary")
    print("="*80)

    text = """को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्।
धर्मज्ञश्च कृतज्ञश्च सत्यवाक्यो दृढव्रतः॥
दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा।
आचार्यमुपसङ्गम्य राजा वचनमब्रवीत्॥
तानुवाच ततो राजा वैरागः प्रभुः।
दुर्योधनपदं प्राप्य वचनं च ब्रवीत्॥"""

    data_path = get_default_data_path()
    analyzer = Chanda(data_path)

    results = analyzer.identify_from_text(text, verse=True, fuzzy=True)
    summary = analyzer.summarize_results(results.result.to_dict())

    print("Input: 3 verses (6 lines)")
    print()

    # Format and display summary
    formatted_summary = Chanda.format_summary(summary)
    print(formatted_summary)
    print()


def example_5_different_scripts():
    """Example 5: Working with different scripts."""
    print("="*80)
    print("Example 5: Different Input/Output Scripts")
    print("="*80)

    # Same verse in different scripts
    devanagari = "रामो राजमणिः सदा विजयते"
    iast = "rāmo rājamaṇiḥ sadā vijayate"
    itrans = "raamo raajamaNiH sadaa vijayate"

    print("Same line in different scripts:")
    print(f"  Devanagari: {devanagari}")
    print(f"  IAST: {iast}")
    print(f"  ITRANS: {itrans}")
    print()

    # All should identify the same meter
    for script_name, text in [("Devanagari", devanagari),
                               ("IAST", iast),
                               ("ITRANS", itrans)]:
        results = analyze_text(text, verse_mode=False)
        if results.result.line:
            result = results.result.line[0].result
            if result.found:
                print(f"{script_name:12s} -> {[name for name, _ in result.chanda]}")

    print()


def example_6_matra_vrtta():
    """Example 6: Mātrā-vṛtta (matra-based meters)."""
    print("="*80)
    print("Example 6: Mātrā-vṛtta Analysis")
    print("="*80)

    # Example of Āryā meter (a mātrā-vṛtta)
    text = "भुजगशयन भयहरण करुणानिधान"

    print(f"Input: {text}")
    print("(Example of mātrā-based meter)")
    print()

    results = analyze_text(text, verse_mode=False, fuzzy=True)

    if results.result.line:
        result = results.result.line[0].result
        print(f"Meter: {[name for name, _ in result.chanda] or 'Unknown'}")
        print(f"Syllables: {result.length}")
        print(f"Mātrā count: {result.matra} (important for mātrā-vṛtta)")
        print(f"Pattern: {' '.join(result.lg)}")

    print()


def main():
    """Run all examples."""
    print("\n")
    print("*" * 80)
    print("Chandojñānam - Verse Analysis Examples")
    print("*" * 80)
    print()

    example_1_bhagavad_gita_verse()
    example_2_multiple_verses()
    example_3_line_mode()
    example_4_statistics_summary()
    example_5_different_scripts()
    example_6_matra_vrtta()

    print("="*80)
    print("All examples completed!")
    print("="*80)


if __name__ == '__main__':
    main()
