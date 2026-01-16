#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line interface for Chandojñānam.

This module provides a CLI tool for identifying Sanskrit meters from
the command line.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional

from .core import Chanda, analyze_line, analyze_text
from .formatter import format_result, format_analysis_summary
from .utils import get_default_data_path, get_supported_meters


def main() -> int:
    """
    Main entry point for the CLI.

    Returns
    -------
    int
        Exit code.
    """
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


def get_input_text(args: argparse.Namespace) -> Optional[str]:
    """
    Get input text from command line arguments.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments.

    Returns
    -------
    str or None
        Input text if present; otherwise ``None``.
    """
    if args.text:
        return args.text
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            return f.read()
    elif args.interactive or not sys.stdin.isatty():
        return sys.stdin.read()
    return None


def perform_analysis(text: str, args: argparse.Namespace) -> Dict[str, Any]:
    """
    Perform meter identification analysis.

    Parameters
    ----------
    text : str
        Input text to analyze.
    args : argparse.Namespace
        Parsed CLI arguments.

    Returns
    -------
    dict
        Result payload tagged with ``type`` and ``result``.
    """
    data_path = args.data_path or get_default_data_path()
    fuzzy = not args.no_fuzzy

    # Check if single line or multiple lines
    lines = text.strip().split('\n')
    if len(lines) == 1 and not args.verse:
        # Single line analysis
        result = analyze_line(
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


def output_results(results: Dict[str, Any], args: argparse.Namespace) -> None:
    """
    Output analysis results in the specified format.

    Parameters
    ----------
    results : dict
        Analysis result payload.
    args : argparse.Namespace
        Parsed CLI arguments.
    """
    output = format_output(results, args)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        print(output)


def format_output(results: Dict[str, Any], args: argparse.Namespace) -> str:
    """
    Format results according to specified output format.

    Parameters
    ----------
    results : dict
        Analysis result payload.
    args : argparse.Namespace
        Parsed CLI arguments.

    Returns
    -------
    str
        Formatted output string.
    """
    if args.format == 'json':
        return format_json_output(results, args)
    elif args.format == 'simple':
        return format_simple_output(results, args)
    else:  # text format
        return format_text_output(results, args)


def _as_dict(value: Any) -> Any:
    """
    Normalize result-like objects into dictionaries.

    Parameters
    ----------
    value : object
        Object with a ``to_dict`` method or a raw dictionary.

    Returns
    -------
    object
        Dictionary representation if available; otherwise the original value.
    """
    if hasattr(value, 'to_dict'):
        return value.to_dict()
    return value


def _format_chanda(result: Dict[str, Any]) -> str:
    """
    Format a chanda list for display.

    Parameters
    ----------
    result : dict
        Line result payload containing a ``chanda`` list.

    Returns
    -------
    str
        Formatted chanda string.
    """
    if not result.get('chanda'):
        return "Not found"
    from .core import Chanda
    return Chanda.format_chanda_list(result.get('chanda', []))


def format_json_output(results: Dict[str, Any], args: argparse.Namespace) -> str:
    """
    Format results as JSON.

    Parameters
    ----------
    results : dict
        Analysis result payload.
    args : argparse.Namespace
        Parsed CLI arguments.

    Returns
    -------
    str
        JSON output string.
    """
    if results['type'] == 'single':
        output_data = _as_dict(results['result'])
    else:
        output_data = _as_dict(results['result']).get('result')

    return json.dumps(output_data, ensure_ascii=False, indent=2)


def format_simple_output(results: Dict[str, Any], args: argparse.Namespace) -> str:
    """
    Format results in simple, concise format.

    Parameters
    ----------
    results : dict
        Analysis result payload.
    args : argparse.Namespace
        Parsed CLI arguments.

    Returns
    -------
    str
        Simple formatted output string.
    """
    output_lines = []

    if results['type'] == 'single':
        result = _as_dict(results['result'])
        if result.get('found'):
            chanda = _format_chanda(result)
            output_lines.append(f"{result['line']}")
            output_lines.append(f"Meter: {chanda}")
            output_lines.append(f"Pattern: {' '.join(result.get('lg', []))}")
        else:
            output_lines.append(f"{result['line']}")
            output_lines.append("Meter: Not found")
            if result.get('fuzzy'):
                top = result['fuzzy'][0]
                top_display = _format_chanda(top)
                output_lines.append(f"Closest: {top_display} ({top['similarity']:.2%})")
    else:
        line_results = _as_dict(results['result']).get('result', {}).get('line', [])
        for line_res in line_results:
            res = line_res['result']
            line = res.get('line', '')
            chanda = _format_chanda(res) if res.get('found') else 'Not found'
            output_lines.append(f"{line} -> {chanda}")

    return '\n'.join(output_lines)


def format_text_output(results: Dict[str, Any], args: argparse.Namespace) -> str:
    """
    Format results in detailed text format.

    Parameters
    ----------
    results : dict
        Analysis result payload.
    args : argparse.Namespace
        Parsed CLI arguments.

    Returns
    -------
    str
        Detailed formatted output string.
    """
    output_lines = []

    if results['type'] == 'single':
        result = results['result']
        output_lines.append(format_result(result))
    else:
        result_dict = _as_dict(results['result']).get('result', {})
        line_results = result_dict.get('line', [])
        verse_results = result_dict.get('verse', [])

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

                for line_idx in verse.get('line_indices', []):
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
            summary = format_analysis_summary({'result': result_dict})
            output_lines.append(summary)

    return '\n'.join(output_lines)


def show_meter_list(data_path: Optional[str] = None) -> None:
    """
    Display list of all supported meters.

    Parameters
    ----------
    data_path : str, optional
        Path to meter definition data directory.
    """
    meters = get_supported_meters(data_path)

    print("Chandojñānam - Supported Sanskrit Meters")
    print("=" * 80)
    print(f"Total meters: {meters.total}")
    print(f"  - Sama-vṛtta (same pattern in all padas): {meters.sama}")
    print(f"  - Ardhasama-vṛtta (alternating padas): {meters.ardhasama}")
    print(f"  - Viṣama-vṛtta (uneven padas): {meters.vishama}")
    print(f"  - Mātrā-vṛtta (matra-based): {meters.matra}")
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
