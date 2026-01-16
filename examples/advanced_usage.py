#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced usage examples for Chandojñānam library.

This script demonstrates advanced features like custom analysis,
pattern manipulation, and batch processing.
"""

from chanda.core import Chanda
from chanda.utils import get_default_data_path, get_supported_meters
from pathlib import Path


def example_1_custom_analysis():
    """Example 1: Custom syllable and pattern analysis."""
    print("="*80)
    print("Example 1: Custom Syllable Analysis")
    print("="*80)

    data_path = get_default_data_path()
    analyzer = Chanda(data_path)

    text = "धर्मक्षेत्रे कुरुक्षेत्रे"

    # Get syllables and LG marks
    syllables, lg_marks = analyzer.mark_lg(text)

    print(f"Text: {text}\n")

    print("Syllable-by-syllable analysis:")
    flat_syllables = [s for line in syllables for word in line for s in word]
    for i, (syl, lg) in enumerate(zip(flat_syllables, lg_marks), 1):
        weight = "Laghu (light)" if lg == 'L' else "Guru (heavy)"
        matra = 1 if lg == 'L' else 2
        print(f"  {i:2d}. '{syl:4s}' -> {lg} ({weight}, {matra} mātrā)")

    print()


def example_2_pattern_conversion():
    """Example 2: Converting between different pattern representations."""
    print("="*80)
    print("Example 2: Pattern Conversion")
    print("="*80)

    data_path = get_default_data_path()
    analyzer = Chanda(data_path)

    # LG pattern
    lg_pattern = "LGGLGLGLLGG"
    print(f"Original LG pattern: {lg_pattern}")

    # Convert to Gana
    gana_pattern = analyzer.lg_to_gana(lg_pattern)
    print(f"Gana notation: {gana_pattern}")

    # Convert back to LG
    lg_back = analyzer.gana_to_lg(gana_pattern)
    print(f"Converted back to LG: {lg_back}")

    # Count mātrā
    matra = analyzer.count_matra(lg_pattern)
    print(f"Mātrā count: {matra}")

    # In Devanagari symbols
    devanagari_gana = gana_pattern.translate(analyzer.ttable_out)
    print(f"Gana in Devanagari: {devanagari_gana}")

    print()


def example_3_fuzzy_matching_details():
    """Example 3: Detailed fuzzy matching analysis."""
    print("="*80)
    print("Example 3: Detailed Fuzzy Matching")
    print("="*80)

    data_path = get_default_data_path()
    analyzer = Chanda(data_path)

    # Intentionally imperfect line
    text = "धर्मक्षेत्रम् कुरुक्षेत्रे समवेता युयुत्सवः"
    print(f"Input (with error): {text}\n")

    result = analyzer.identify_line(text, fuzzy=True, k=5)

    if not result.found:
        print("No exact match. Top 5 fuzzy matches:\n")

        from chanda import format_chanda_list
        for i, match in enumerate(result.fuzzy, 1):
            print(f"{i}. {format_chanda_list(match['chanda'])}")
            print(f"   Similarity: {match['similarity']:.2%}")
            print(f"   Edit cost: {match['cost']}")
            print(f"   Target pattern: {match['gana']}")

            # Show suggestions
            if match['suggestion']:
                print("   Suggested corrections:")
                for line in match['suggestion']:
                    for word in line:
                        corrections = ' '.join(word)
                        print(f"     {corrections}")

            print()

    print()


def example_4_batch_processing():
    """Example 4: Batch process multiple texts."""
    print("="*80)
    print("Example 4: Batch Processing")
    print("="*80)

    data_path = get_default_data_path()
    analyzer = Chanda(data_path)

    texts = [
        "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्",
        "रामो राजमणिः सदा विजयते रामं रमेशं भजे",
        "वन्दे मातरम् सुजलां सुफलां मलयजशीतलाम्",
        "अहं ब्रह्मास्मि तत्त्वमसि अयमात्मा ब्रह्म",
    ]

    print("Batch analyzing 4 lines...\n")

    results = []
    for i, text in enumerate(texts, 1):
        result = analyzer.identify_line(text, fuzzy=True)
        results.append((text, result))

        meter = [name for name, _ in result.chanda] if result.found else 'Not found'
        print(f"{i}. {meter}")
        print(f"   {text[:50]}...")

    print(f"\nProcessed {len(results)} lines successfully.")
    print()


def example_5_meter_statistics():
    """Example 5: Get database statistics."""
    print("="*80)
    print("Example 5: Meter Database Statistics")
    print("="*80)

    meters = get_supported_meters()

    print("Chandojñānam Meter Database:")
    print(f"  Total unique meters: {meters.total}")
    print(f"  Sama-vṛtta: {meters.sama}")
    print(f"  Ardhasama-vṛtta: {meters.ardhasama}")
    print(f"  Viṣama-vṛtta: {meters.vishama}")
    print(f"  Mātrā-vṛtta: {meters.matra}")

    print()


def example_6_custom_meter_lookup():
    """Example 6: Look up specific meter patterns."""
    print("="*80)
    print("Example 6: Custom Meter Lookup")
    print("="*80)

    data_path = get_default_data_path()
    analyzer = Chanda(data_path)

    # Look up what meters match a specific pattern
    pattern = "LGLLGLLG"  # Anuṣṭup pattern
    print(f"Looking up meters with pattern: {pattern}\n")

    if pattern in analyzer.SINGLE_CHANDA:
        meters = analyzer.SINGLE_CHANDA[pattern]
        print(f"Found {len(meters)} meter(s):")
        for name, pada in meters:
            pada_str = f"(पाद {pada[0]})" if pada and pada[0] else ""
            print(f"  - {name} {pada_str}")
    else:
        print("No meters found for this pattern.")

    print()


def example_7_file_processing():
    """Example 7: Process a file (simulated)."""
    print("="*80)
    print("Example 7: File Processing Simulation")
    print("="*80)

    # Simulated file content
    file_content = """को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्।
धर्मज्ञश्च कृतज्ञश्च सत्यवाक्यो दृढव्रतः॥

दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा।
आचार्यमुपसङ्गम्य राजा वचनमब्रवीत्॥"""

    data_path = get_default_data_path()
    analyzer = Chanda(data_path)

    print("Processing simulated file content...\n")

    results = analyzer.identify_from_text(
        file_content,
        verse=True,
        fuzzy=True
    )

    # Get summary
    summary = analyzer.summarize_results(results.result.to_dict())

    print("File Statistics:")
    counts = summary['count']
    print(f"  Total lines: {counts['line']}")
    print(f"  Total verses: {counts['verse']}")
    print(f"  Exact matches: {counts['match_line']}")
    print(f"  Fuzzy matches: {counts['fuzzy_line']}")
    print(f"  Syllable errors: {counts['mismatch_syllable']}")

    print()


def example_8_error_handling():
    """Example 8: Handling edge cases and errors."""
    print("="*80)
    print("Example 8: Error Handling")
    print("="*80)

    data_path = get_default_data_path()
    analyzer = Chanda(data_path)

    # Test various edge cases
    test_cases = [
        ("Empty string", ""),
        ("Single word", "धर्म"),
        ("Numbers", "123 456"),
        ("Mixed script", "dharma क्षेत्रे"),
    ]

    print("Testing edge cases:\n")

    for description, text in test_cases:
        print(f"{description}: '{text}'")
        try:
            if text:
                result = analyzer.identify_line(text, fuzzy=False)
                if result:
                    print(f"  Result: {'Found' if result.found else 'Not found'}")
                else:
                    print("  Result: Empty result")
            else:
                print("  Result: Skipped (empty)")
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")

        print()

    print()


def main():
    """Run all examples."""
    print("\n")
    print("*" * 80)
    print("Chandojñānam - Advanced Usage Examples")
    print("*" * 80)
    print()

    example_1_custom_analysis()
    example_2_pattern_conversion()
    example_3_fuzzy_matching_details()
    example_4_batch_processing()
    example_5_meter_statistics()
    example_6_custom_meter_lookup()
    example_7_file_processing()
    example_8_error_handling()

    print("="*80)
    print("All examples completed!")
    print("="*80)


if __name__ == '__main__':
    main()
