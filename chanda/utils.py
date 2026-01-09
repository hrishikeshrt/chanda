"""
Utility functions for the Chandojñānam library.

This module provides convenient wrapper functions and helpers for common operations.
"""

import os
from typing import Dict, Any, Optional

from .core import Chanda


def get_default_data_path() -> str:
    """
    Get the default path to meter definition data files.

    Returns:
        str: Absolute path to the data directory within the package
    """
    return os.path.join(os.path.dirname(__file__), 'data')


def identify_meter(
    text: str,
    fuzzy: bool = True,
    k: int = 10,
    output_scheme: Optional[str] = None,
    data_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenient function to identify meter from a single line of Sanskrit text.

    This is a simplified wrapper around the Chanda class for quick meter identification.

    Args:
        text (str): Sanskrit text (single line) in any supported script
        fuzzy (bool): Enable fuzzy matching if exact match not found (default: True)
        k (int): Maximum number of fuzzy matches to return (default: 10)
        output_scheme (str, optional): Transliteration scheme for output
                                     (e.g., 'iast', 'itrans', 'devanagari')
        data_path (str, optional): Path to meter definition data directory
                                  If None, uses package default

    Returns:
        dict: Identification result containing:
            - found (bool): Whether exact match was found
            - chanda (list): List of (meter_name, pada) tuples
            - syllables (list): Syllables in the text
            - lg (list): Laghu-Guru pattern
            - gana (str): Gana notation
            - length (int): Syllable count
            - matra (int): Mātrā count
            - jaati (tuple): Jāti classification
            - fuzzy (list): Fuzzy matches if enabled and no exact match
            - display_* : Formatted display versions

    Example:
        >>> result = identify_meter("इक्ष्वाकुवंशप्रभवो रामो नाम जनैः श्रुतः")
        >>> print(result['display_chanda'])
        'Anuṣṭup (पाद 1)'
        >>> print(result['display_gana'])
        'नभजलगलग'
        >>> print(result['matra'])
        32

    Raises:
        ValueError: If text contains more than one line
    """
    if data_path is None:
        data_path = get_default_data_path()

    analyzer = Chanda(data_path)
    result = analyzer.identify_line(text, fuzzy=fuzzy, k=k)

    if output_scheme:
        # Apply output scheme if specified
        result['display_scheme'] = output_scheme

    return result


def analyze_text(
    text: str,
    verse_mode: bool = False,
    fuzzy: bool = True,
    output_scheme: Optional[str] = None,
    data_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze multi-line Sanskrit text for meter identification.

    Args:
        text (str): Sanskrit text (can be multiple lines)
        verse_mode (bool): If True, group lines into 4-line verses (default: False)
        fuzzy (bool): Enable fuzzy matching (default: True)
        output_scheme (str, optional): Transliteration scheme for output
        data_path (str, optional): Path to meter definition data directory

    Returns:
        dict: Analysis results containing:
            - result: Dict with 'line' and 'verse' results
            - path: Dict with 'json' and 'txt' file paths (if saved)

    Example:
        >>> text = '''इक्ष्वाकुवंशप्रभवो रामो नाम जनैः श्रुतः।
        ... मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय॥'''
        >>> results = analyze_text(text, verse_mode=True)
        >>> for line in results['result']['line']:
        ...     print(line['result']['display_chanda'])
    """
    if data_path is None:
        data_path = get_default_data_path()

    analyzer = Chanda(data_path)
    results = analyzer.identify_from_text(
        text,
        verse=verse_mode,
        fuzzy=fuzzy,
        scheme=output_scheme
    )

    return results


def format_result(result: Dict[str, Any]) -> str:
    """
    Format meter identification result as human-readable text.

    Args:
        result (dict): Result dictionary from identify_line or identify_meter

    Returns:
        str: Formatted multi-line string representation

    Example:
        >>> result = identify_meter("इक्ष्वाकुवंशप्रभवो रामो नाम जनैः श्रुतः")
        >>> print(format_result(result))
        इक्ष्वाकुवंशप्रभवो रामो नाम जनैः श्रुतः
            Syllables: ['धर्', 'म', 'क्षे', 'त्रे', 'कु', 'रु', 'क्षे', 'त्रे', ...]
            LG: ['ग', 'ल', 'ग', 'ग', 'ल', 'ग', 'ल', 'ग']
            Gana: नभजलगलग
            Counts: 8 letters, 16 morae
            Chanda: Anuṣṭup (पाद 1)
            Jaati: Anuṣṭup
    """
    return Chanda.format_line_result(result)


def get_supported_meters(data_path: Optional[str] = None) -> Dict[str, int]:
    """
    Get list of all supported meters in the database.

    Args:
        data_path (str, optional): Path to meter definition data directory

    Returns:
        dict: Dictionary with meter type counts:
            - total: Total number of meters
            - sama: Sama-vṛtta count
            - ardhasama: Ardhasama-vṛtta count
            - vishama: Viṣama-vṛtta count
            - matra: Mātrā-vṛtta count

    Example:
        >>> meters = get_supported_meters()
        >>> print(f"Total meters: {meters['total']}")
        >>> print(f"Sama meters: {meters['sama']}")
    """
    if data_path is None:
        data_path = get_default_data_path()

    analyzer = Chanda(data_path)

    # Count unique meters
    all_meters = set()
    sama_meters = set()
    multi_meters = set()
    matra_meters = set()

    for chanda_list in analyzer.SINGLE_CHANDA.values():
        for name, pada in chanda_list:
            sama_meters.add(name)
            all_meters.add(name)

    for chanda_list in analyzer.MULTI_CHANDA.values():
        for name, pada in chanda_list:
            multi_meters.add(name)
            all_meters.add(name)

    for chanda_list in analyzer.MATRA_CHANDA.values():
        for name, pada in chanda_list:
            matra_meters.add(name)
            all_meters.add(name)

    return {
        'total': len(all_meters),
        'sama': len(sama_meters),
        'ardhasama_vishama': len(multi_meters),
        'matra': len(matra_meters)
    }
