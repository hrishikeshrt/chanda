#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic usage examples for Chandojñānam library.

This script demonstrates simple meter identification scenarios.
"""

from chanda import identify_meter

def example_1_single_line():
    """Example 1: Identify meter from a single line."""
    print("="*80)
    print("Example 1: Single Line Identification")
    print("="*80)

    text = "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"
    print(f"Input: {text}\n")

    result = identify_meter(text)

    if result.found:
        print(f"Meter found: {[name for name, _ in result.chanda]}")
        print(f"Pattern (LG): {' '.join(result.lg)}")
        print(f"Gana notation: {result.gana}")
        print(f"Syllable count: {result.length}")
        print(f"Mātrā count: {result.matra}")
        print(f"Jāti: {result.jaati}")
    else:
        print("No exact match found.")

    print()


def example_2_romanized_input():
    """Example 2: Using romanized (IAST) input."""
    print("="*80)
    print("Example 2: Romanized Input (IAST)")
    print("="*80)

    text = "rāmo rājamaṇiḥ sadā vijayate rāmaṃ rameśaṃ bhaje"
    print(f"Input: {text}\n")

    result = identify_meter(text)

    if result.found:
        print(f"Meter: {[name for name, _ in result.chanda]}")
        print(f"Pattern: {' '.join(result.lg)}")
    else:
        print("No exact match found.")

    print()


def example_3_fuzzy_matching():
    """Example 3: Fuzzy matching for imperfect verses."""
    print("="*80)
    print("Example 3: Fuzzy Matching")
    print("="*80)

    # This line has a slight metrical error
    text = "धर्मक्षेत्रे कुरुक्षेत्रम् समवेता युयुत्सवः"
    print(f"Input: {text}")
    print("(Note: This has a metrical error - 'कुरुक्षेत्रम्' instead of 'कुरुक्षेत्रे')\n")

    result = identify_meter(text, fuzzy=True)

    if result.found:
        print(f"Exact match: {[name for name, _ in result.chanda]}")
    else:
        print("No exact match found. Checking fuzzy matches...\n")

        if result.fuzzy:
            print("Top fuzzy matches:")
            from chanda import format_chanda_list
            for i, match in enumerate(result.fuzzy[:3], 1):
                print(f"\n{i}. {format_chanda_list(match['chanda'])}")
                print(f"   Similarity: {match['similarity']:.2%}")
                print(f"   Cost: {match['cost']} syllable(s)")
                print(f"   Pattern: {match['gana']}")

    print()


def example_4_different_meters():
    """Example 4: Identifying different types of meters."""
    print("="*80)
    print("Example 4: Different Meter Types")
    print("="*80)

    examples = [
        ("Anuṣṭup/Śloka", "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"),
        ("Indravajrā", "विबुधैः सुरवरैः सततं पूजनीयम्"),
        ("Upendravajrā", "रामं दशरथस्यात्मजं भूमिपतिं"),
        ("Vasantatilakā", "स्यन्दनेषु च शङ्खांश्च दध्मुः पार्थाः महारथाः"),
    ]

    for meter_name, text in examples:
        print(f"\n{meter_name}:")
        print(f"  {text}")
        result = identify_meter(text)
        if result.found:
            print(f"  ✓ Identified: {[name for name, _ in result.chanda]}")
            print(f"    Pattern: {result.gana}")
        else:
            print(f"  ✗ Not identified exactly")

    print()


def example_5_matra_counting():
    """Example 5: Mātrā counting for mātrā-vṛtta."""
    print("="*80)
    print("Example 5: Mātrā Counting")
    print("="*80)

    text = "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"
    print(f"Input: {text}\n")

    result = identify_meter(text)

    print("Syllable breakdown:")
    for i, (syllable, lg) in enumerate(zip(result.syllables, result.lg), 1):
        matra = 1 if lg == 'ल' else 2  # laghu = 1, guru = 2
        print(f"  {i:2d}. {syllable:4s} -> {lg} ({matra} mātrā)")

    print(f"\nTotal syllables: {result.length}")
    print(f"Total mātrā: {result.matra}")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("*" * 80)
    print("Chandojñānam - Basic Usage Examples")
    print("*" * 80)
    print()

    example_1_single_line()
    example_2_romanized_input()
    example_3_fuzzy_matching()
    example_4_different_meters()
    example_5_matra_counting()

    print("="*80)
    print("All examples completed!")
    print("="*80)


if __name__ == '__main__':
    main()
