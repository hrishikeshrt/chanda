#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line interface for Chandojñānam.

This module provides a CLI tool for identifying Sanskrit meters from the command line.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from .core import Chanda
from .utils import identify_meter, analyze_text, format_result, get_default_data_path, get_supported_meters


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog='chanda',
        description='Sanskrit Meter Identification Tool',
        epilog='For more information, visit: https://github.com/hrishikeshrt/chanda'
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        'text',
        nargs='?',
        help='Sanskrit text to analyze (single line or verse)'
    )
    input_group.add_argument(
        '-f', '--file',
        type=str,
        metavar='FILE',
        help='Input file containing Sanskrit text'
    )
    input_group.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Interactive mode - read from stdin'
    )

    # Analysis options
    parser.add_argument(
        '-v', '--verse',
        action='store_true',
        help='Verse mode: group lines into 4-line verses'
    )
    parser.add_argument(
        '--no-fuzzy',
        action='store_true',
        help='Disable fuzzy matching (only exact matches)'
    )
    parser.add_argument(
        '-k', '--top-k',
        type=int,
        default=10,
        metavar='K',
        help='Number of fuzzy matches to show (default: 10)'
    )

    # Output options
    parser.add_argument(
        '-o', '--output',
        type=str,
        metavar='FILE',
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'simple'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '-s', '--scheme',
        type=str,
        choices=['devanagari', 'iast', 'itrans', 'hk', 'slp1', 'wx', 'velthuis'],
        help='Output transliteration scheme'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary statistics'
    )

    # Data options
    parser.add_argument(
        '--data-path',
        type=str,
        metavar='PATH',
        help='Path to meter definition data directory'
    )

    # Info options
    parser.add_argument(
        '--list-meters',
        action='store_true',
        help='List all supported meters and exit'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Handle list-meters option
    if args.list_meters:
        show_meter_list(args.data_path)
        return 0

    # Get input text
    text = get_input_text(args)
    if not text:
        parser.print_help()
        return 1

    # Perform analysis
    try:
        results = perform_analysis(text, args)
        output_results(results, args)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def get_input_text(args) -> Optional[str]:
    """Get input text from command line arguments."""
    if args.text:
        return args.text
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            return f.read()
    elif args.interactive or not sys.stdin.isatty():
        return sys.stdin.read()
    return None


def perform_analysis(text: str, args):
    """Perform meter identification analysis."""
    data_path = args.data_path or get_default_data_path()
    fuzzy = not args.no_fuzzy

    # Check if single line or multiple lines
    lines = text.strip().split('\n')
    if len(lines) == 1 and not args.verse:
        # Single line analysis
        result = identify_meter(
            text,
            fuzzy=fuzzy,
            output_scheme=args.scheme,
            data_path=data_path
        )
        return {'type': 'single', 'result': result}
    else:
        # Multi-line analysis
        results = analyze_text(
            text,
            verse_mode=args.verse,
            fuzzy=fuzzy,
            output_scheme=args.scheme,
            data_path=data_path
        )
        return {'type': 'multi', 'result': results}


def output_results(results, args):
    """Output analysis results in the specified format."""
    output = format_output(results, args)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        print(output)


def format_output(results, args) -> str:
    """Format results according to specified output format."""
    if args.format == 'json':
        return format_json_output(results, args)
    elif args.format == 'simple':
        return format_simple_output(results, args)
    else:  # text format
        return format_text_output(results, args)


def format_json_output(results, args) -> str:
    """Format results as JSON."""
    if results['type'] == 'single':
        output_data = results['result']
    else:
        output_data = results['result']['result']

    return json.dumps(output_data, ensure_ascii=False, indent=2)


def format_simple_output(results, args) -> str:
    """Format results in simple, concise format."""
    output_lines = []

    if results['type'] == 'single':
        result = results['result']
        if result.get('found'):
            chanda = result.get('display_chanda', 'Unknown')
            output_lines.append(f"{result['display_line']}")
            output_lines.append(f"Meter: {chanda}")
            output_lines.append(f"Pattern: {' '.join(result.get('display_lg', []))}")
        else:
            output_lines.append(f"{result['display_line']}")
            output_lines.append("Meter: Not found")
            if result.get('fuzzy'):
                top = result['fuzzy'][0]
                output_lines.append(f"Closest: {top['display_chanda']} ({top['similarity']:.2%})")
    else:
        line_results = results['result']['result']['line']
        for line_res in line_results:
            res = line_res['result']
            line = res.get('display_line', '')
            chanda = res.get('display_chanda', 'Unknown') if res.get('found') else 'Not found'
            output_lines.append(f"{line} -> {chanda}")

    return '\n'.join(output_lines)


def format_text_output(results, args) -> str:
    """Format results in detailed text format."""
    output_lines = []

    if results['type'] == 'single':
        result = results['result']
        output_lines.append(format_result(result))
    else:
        line_results = results['result']['result']['line']
        verse_results = results['result']['result'].get('verse', [])

        if verse_results:
            # Verse mode output
            for verse_idx, verse in enumerate(verse_results, 1):
                output_lines.append(f"{'='*80}")
                output_lines.append(f"Verse {verse_idx}")
                output_lines.append(f"{'='*80}")
                if verse.get('chanda'):
                    best_matches, score = verse['chanda']
                    output_lines.append(
                        f"Best meter(s): {' / '.join(best_matches)} (score: {score})"
                    )
                else:
                    output_lines.append("Best meter(s): Not found")
                output_lines.append("")

                for line_idx in verse['lines']:
                    line_res = line_results[line_idx]
                    output_lines.append(format_result(line_res['result']))
                    output_lines.append("")

                output_lines.append("")
        else:
            # Line mode output
            for idx, line_res in enumerate(line_results, 1):
                output_lines.append(f"Line {idx}:")
                output_lines.append(format_result(line_res['result']))
                output_lines.append("")

        # Add summary if requested
        if args.summary and len(line_results) > 1:
            output_lines.append(f"{'='*80}")
            output_lines.append("SUMMARY")
            output_lines.append(f"{'='*80}")
            from .core import Chanda
            summary = Chanda.format_summary(
                Chanda(args.data_path or get_default_data_path()).summarize_results(
                    results['result']['result']
                )
            )
            output_lines.append(summary)

    return '\n'.join(output_lines)


def show_meter_list(data_path: Optional[str] = None):
    """Display list of all supported meters."""
    meters = get_supported_meters(data_path)

    print("Chandojñānam - Supported Sanskrit Meters")
    print("=" * 80)
    print(f"Total meters: {meters['total']}")
    print(f"  - Sama-vṛtta (same pattern in all padas): {meters['sama']}")
    print(f"  - Ardhasama/Viṣama-vṛtta (varying patterns): {meters['ardhasama_vishama']}")
    print(f"  - Mātrā-vṛtta (matra-based): {meters['matra']}")
    print()
    print("Examples of popular meters:")
    print("  - Anuṣṭup (श्लोक)")
    print("  - Indravajrā")
    print("  - Upendravajrā")
    print("  - Vasantatilakā")
    print("  - Mālinī")
    print("  - Śārdūlavikrīḍita")
    print("  - Āryā (मात्रा-वृत्त)")
    print()
    print("Use --help for more information on usage.")


if __name__ == '__main__':
    sys.exit(main())
