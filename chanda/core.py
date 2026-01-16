#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core module for Sanskrit meter identification and analysis.

Extended Summary
----------------
Defines the main ``Chanda`` class and the public helper functions
for identifying meters from lines or full texts.

Notes
-----
Author: Hrishikesh Terdalkar
Created on Fri Jan 22 22:23:37 2021
"""

###############################################################################

import os
import re
import csv
import json
import hashlib
import functools
import itertools
from typing import Tuple, List, Dict, Optional, Any, Union
from typing import Iterator

from collections import defaultdict, Counter

import Levenshtein as Lev

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

import sanskrit_text as skt

from .constants import (
    MAX_CACHE,
    DEFAULT_VERSE_LINES,
    SyllableWeight,
    GanaSymbol
)
from .analyzer import get_chanda_analyzer
from .display import (
    format_chanda_pada as _format_chanda_pada,
    format_chanda_list as _format_chanda_list,
    format_line_result as _format_line_result,
    format_summary as _format_summary,
)
from .processor import SanskritTextProcessor
from .types import ChandaResult, LineResult, VerseResult, AnalysisResult, TextAnalysisResult

###############################################################################


Syllables = List[List[List[str]]]


class Chanda:
    """
    Chanda (Sanskrit Meter) Identifier.

    This class provides comprehensive meter identification and analysis for Sanskrit poetry,
    supporting Sama-vṛtta, Ardhasama-vṛtta, Viṣama-vṛtta, and Mātrā-vṛtta meters.

    Parameters
    ----------
    data_path : str
        Path to the meter definition data directory.
    symbols : str, optional
        Custom gaṇa symbol ordering for output formatting.
    language : str, optional
        Language code for prosody rules (``'sanskrit'``, ``'vedic'``, ``'prakrit'``).
    """

    # Build gaṇa pattern mappings
    GANA_PATTERNS = {
        GanaSymbol.Y.value: f'{SyllableWeight.L.value}{SyllableWeight.G.value}{SyllableWeight.G.value}',
        GanaSymbol.R.value: f'{SyllableWeight.G.value}{SyllableWeight.L.value}{SyllableWeight.G.value}',
        GanaSymbol.T.value: f'{SyllableWeight.G.value}{SyllableWeight.G.value}{SyllableWeight.L.value}',
        GanaSymbol.N.value: f'{SyllableWeight.L.value}{SyllableWeight.L.value}{SyllableWeight.L.value}',
        GanaSymbol.B.value: f'{SyllableWeight.G.value}{SyllableWeight.L.value}{SyllableWeight.L.value}',
        GanaSymbol.J.value: f'{SyllableWeight.L.value}{SyllableWeight.G.value}{SyllableWeight.L.value}',
        GanaSymbol.S.value: f'{SyllableWeight.L.value}{SyllableWeight.L.value}{SyllableWeight.G.value}',
        GanaSymbol.M.value: f'{SyllableWeight.G.value}{SyllableWeight.G.value}{SyllableWeight.G.value}'
    }

    # Convenience constants for internal use
    L = SyllableWeight.L.value
    G = SyllableWeight.G.value
    SYMBOLS = ''.join(s.value for s in GanaSymbol) + L + G
    GANA = GANA_PATTERNS

    def __init__(
        self,
        data_path: str,
        symbols: str = 'यरतनभजसमलग',
        language: str = 'sanskrit'
    ) -> None:
        self.input_map = dict(zip(symbols, self.SYMBOLS))
        self.output_map = dict(zip(self.SYMBOLS, symbols))
        self.ttable_in = str.maketrans(self.input_map)
        self.ttable_out = str.maketrans(self.output_map)
        self.gana = self.GANA.copy()
        self.gana_inv = {
            v: k for k, v in self.gana.items()
        }

        # Data Path
        self.data_path = data_path

        # Chanda analyzer (language-specific)
        self.chanda_analyzer = get_chanda_analyzer(language)

        # Definitions
        self.CHANDA = defaultdict(list)
        self.SINGLE_CHANDA = defaultdict(list)
        self.MULTI_CHANDA = defaultdict(list)
        self.JAATI = defaultdict(list)
        self.SPLITS = defaultdict(list)
        self.MATRA_CHANDA = defaultdict(list)
        self.MATRA_PATTERNS = {}

        # Read Data
        self.read_data()

    ###########################################################################

    @functools.lru_cache(maxsize=MAX_CACHE)
    def mark_syllable_weights(self, text: str) -> Tuple[Syllables, List[str]]:
        """
        Mark laghu-guru using the language-specific prosody analyzer.

        Parameters
        ----------
        text : str
            Input text string.

        Returns
        -------
        list
            Nested syllable structure from the tokenizer.
        list[str]
            Laghu-guru marks aligned with flattened syllables.
        """
        return self.chanda_analyzer.mark_syllable_weights(text)

    # ----------------------------------------------------------------------- #

    def _scan_line(
        self,
        line: str,
        clean: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Scan a line to extract syllables and laghu-guru markers.

        Parameters
        ----------
        line : str
            Input line.
        clean : bool, optional
            Whether to clean the line before scanning.

        Returns
        -------
        dict or None
            Dictionary with syllables, ``lg_marks``, and ``lg_str``, or ``None``
            if the scan is empty.
        """
        if clean:
            line = skt.clean(line)
        syllables, lg_marks = self.mark_syllable_weights(line)
        lg_str = ''.join(lg_marks)
        if not lg_str:
            return None
        flat_syllables = [s for ln in syllables for w in ln for s in w]
        return {
            'syllables': flat_syllables,
            'syllables_nested': syllables,
            'lg_marks': lg_marks,
            'lg_str': lg_str
        }

    def _empty_result(
        self,
        line: str,
        scheme: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build a consistent empty result payload for invalid/empty input lines.

        Parameters
        ----------
        line : str
            Original line in the output scheme.
        scheme : str or None, optional
            Output transliteration scheme.

        Returns
        -------
        dict
            Empty result payload.
        """
        return {
            'found': False,
            'line': line,
            'scheme': scheme,
            'syllables': [],
            'lg': [],
            'gana': "",
            'length': 0,
            'matra': 0,
            'chanda': [],
            'jaati': [],
            'fuzzy': []
        }

    def _lookup_lg(
        self,
        lg_str: str,
        dictionary: Dict[str, List[Tuple[str, Tuple]]]
    ) -> Tuple[str, List[Tuple[str, Tuple]], bool]:
        """
        Lookup a laghu-guru pattern in a dictionary with last-syllable fallback.

        Parameters
        ----------
        lg_str : str
            Laghu-guru string.
        dictionary : dict
            Mapping of patterns to meter lists.

        Returns
        -------
        tuple
            ``(matched_lg_str, chanda_list, found)``.
        """
        if lg_str in dictionary:
            return lg_str, dictionary.get(lg_str, []), True
        if lg_str.endswith(self.L):
            alt = lg_str[:-1] + self.G
            if alt in dictionary:
                return alt, dictionary.get(alt, []), True
        return lg_str, [], False

    def _build_match(
        self,
        scan: Dict[str, Any],
        multi: bool = False
    ) -> Dict[str, Any]:
        """
        Build match details for a scanned line.

        Parameters
        ----------
        scan : dict
            Output from ``_scan_line``.
        multi : bool, optional
            Whether to use multi-pada dictionary.

        Returns
        -------
        dict
            Match dictionary compatible with ``find_direct_match`` output.
        """
        dictionary = self.MULTI_CHANDA if multi else self.SINGLE_CHANDA
        match_lg, chanda_list, found = self._lookup_lg(
            scan['lg_str'],
            dictionary
        )

        chanda = []
        jaati = []
        gana = []
        length = []
        matra = []

        if found:
            chanda += chanda_list

        if not multi:
            jaati = self.JAATI.get(len(match_lg), self.JAATI[-1])
            gana = [self.lg_to_gana(match_lg)]
            length = [str(len(match_lg))]
            matra = [str(self.count_matra(match_lg))]
        elif found:
            splits = self.SPLITS.get(match_lg, [])
            jaati = [
                "(" + ', '.join(
                    ' / '.join(self.JAATI.get(len(split), self.JAATI[-1]))
                    for split in split_group
                ) + ")"
                for split_group in splits
            ]
            gana = [
                f"({', '.join(self.lg_to_gana(s) for s in split_group)})"
                for split_group in splits
            ]
            length = [
                f"({' + '.join(str(len(s)) for s in split_group)})"
                for split_group in splits
            ]
            matra = [
                f"({' + '.join(str(self.count_matra(s)) for s in split_group)})"
                for split_group in splits
            ]

        return {
            'found': found,
            'syllables': scan['syllables'],
            'lg': scan['lg_marks'],
            'gana': gana,
            'chanda': chanda,
            'jaati': jaati,
            'length': length,
            'matra': matra
        }

    # ----------------------------------------------------------------------- #

    def _matra_options_from_result(
        self,
        result: Union[Dict[str, Any], ChandaResult]
    ) -> List[int]:
        """
        Compute possible mātrā counts for a line result.

        Parameters
        ----------
        result : dict or ChandaResult
            Line result payload or object.

        Returns
        -------
        list[int]
            Possible mātrā counts accounting for terminal laghu/guru.
        """
        if isinstance(result, ChandaResult):
            lg_marks = result.lg or []
            base = result.matra
        else:
            lg_marks = result.get('lg') or []
            base = result.get('matra')
        if not lg_marks:
            return []

        lg_str = ''.join(self.input_map.get(m, m) for m in lg_marks if m)
        if not lg_str:
            return []

        if not isinstance(base, int):
            base = self.count_matra(lg_str)

        options = [base]
        last = lg_str[-1]
        if last == self.L:
            options.append(base + 1)
        elif last == self.G and base > 0:
            options.append(base - 1)

        return list(dict.fromkeys(options))

    def _iter_matra_tuples(self, matra_options: List[List[int]]) -> Iterator[Tuple[int, ...]]:
        """
        Yield all mātrā combinations from per-line options.

        Parameters
        ----------
        matra_options : list[list[int]]
            Per-line mātrā count options.

        Returns
        -------
        iterator
            Iterator of mātrā tuples across all combinations.
        """
        if not matra_options:
            return iter(())
        return (tuple(combo) for combo in itertools.product(*matra_options))

    # ----------------------------------------------------------------------- #

    def lg_to_gana(self, lg_str: str) -> str:
        """
        Transform a laghu-guru string into gaṇa notation.

        Parameters
        ----------
        lg_str : str
            Laghu-guru pattern string.

        Returns
        -------
        str
            Gaṇa notation string.
        """
        gana = []
        for i in range(0, len(lg_str), 3):
            group = lg_str[i:i+3]
            gana.append(self.gana_inv.get(group, group))
        gana_str = ''.join(gana)

        return gana_str

    def gana_to_lg(self, gana_str: str) -> str:
        """
        Transform a gaṇa string into a laghu-guru string.

        Parameters
        ----------
        gana_str : str
            Gaṇa notation string.

        Returns
        -------
        str
            Laghu-guru pattern string.
        """
        return gana_str.translate(str.maketrans(self.gana))

    # ----------------------------------------------------------------------- #

    def count_matra(self, gana_str: str) -> int:
        """
        Count mātrās from a gaṇa or laghu-guru string.

        Parameters
        ----------
        gana_str : str
            Gaṇa or laghu-guru string.

        Returns
        -------
        int
            Mātrā count.
        """
        lg_str = self.gana_to_lg(gana_str)
        return lg_str.count(self.L) + lg_str.count(self.G) * 2

    ###########################################################################

    def read_jaati(self, file: str) -> Dict[int, Tuple[str, ...]]:
        """
        Read jāti list from a CSV file.

        Parameters
        ----------
        file : str
            Path to the CSV file containing jāti definitions.

        Returns
        -------
        dict
            Mapping of letter counts to jāti names.

        Notes
        -----
        The CSV is expected to have:
        - First column: number of letters
        - Second column: jāti name(s)
        """
        jaati = defaultdict(list)
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = True
            for row in reader:
                if header:
                    header = False
                    continue
                letter_count = int(row[0].strip())
                names = [c.strip() for c in row[1].split(',')]
                jaati[letter_count] = tuple(names)

        self.JAATI.update(jaati)
        return jaati

    def read_chanda_definitions(self, chanda_file: str) -> Dict[str, List[Tuple[str, Tuple]]]:
        """
        Read definitions of chanda from a CSV file.

        Parameters
        ----------
        chanda_file : str
            Path to the CSV file containing chanda definitions.

        Returns
        -------
        dict
            Mapping of laghu-guru patterns to meter lists.

        Notes
        -----
        The CSV is expected to have at least 3 columns:
        - First column: name(s) of chanda/vṛtta
        - Second column: pada
        - Third column: gaṇa string
        Remaining columns are ignored.
        """
        chanda = defaultdict(list)
        multi_chanda = defaultdict(list)
        splits = defaultdict(list)

        chanda_pada = defaultdict(dict)

        with open(chanda_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = True
            for row in reader:
                if header:
                    header = False
                    continue
                if not row[0].strip():
                    continue

                # `meters` is a tuple since we need it to be hashable
                # for use as a key in the dictionary `chanda_pada`
                names = tuple(c.strip() for c in row[0].split(','))
                pada = row[1].strip()
                # meters = ((chanda, pada), ...)
                meters = tuple((c, (pada,)) for c in names)
                lakshana = ''.join(row[2].split())
                lakshana = lakshana.translate(self.ttable_in)
                lakshana = self.gana_to_lg(lakshana)
                lakshana = lakshana.replace(
                    '-', f"[{self.L}{self.G}]"
                )
                # NOTE:
                # First, if pada is None => Sama Vṛtta => Same lakshana for 1-4
                # if pada == 1, initialize all 4 pada (in case 3 and 4 are absent)
                # if pada == 2 (which should appear after pada == 1 appears), set 2, 4 same as 2 (in case 3 and 4 are absent)
                # if 3 or 4 exists independently, it will overwrite
                # TODO: Do we need to improve this ad-hoc fix?
                # Main reason for such processing is that lines are processed 1-by-1
                # One solution can be to accumulate pada lakshana for all chanda,
                # or explicitly mention pada for which it is valid in definitions
                # (e.g. 1/2/3/4 for sama, 1/3, 2/4 for ardhasama)
                # TODO: when multi_chanda match exists, that should get 2x or 4x weightage
                # compared to single. i.e. 2 errors in 1 pada are more severe than 2 errors in 2 padas or 3-4 errors in 4 padas
                # so their "relative" edit distance may need to be divided by 2 or 4.

                if not pada or pada == '1':
                    for pada_id in ('1', '2', '3', '4'):
                        chanda_pada[names][pada_id] = lakshana
                elif pada == '2':
                    for pada_id in ('2', '4'):
                        chanda_pada[names][pada_id] = lakshana
                else: # pada = '3' or '4'
                    chanda_pada[names][pada] = lakshana

                if lakshana:
                    chanda[lakshana].extend(meters)

        for _chanda_names, _pada_lakshana in chanda_pada.items():
            multi_pada = []
            multi_lakshana = []
            for _pada, _lakshana in _pada_lakshana.items():
                multi_pada.append(_pada)
                multi_lakshana.append(_lakshana)

                if len(multi_pada) == 2 or len(multi_pada) == 4:
                    # add signature for 1+2, 1+2+3+4
                    names = tuple(
                        (_name, tuple(multi_pada)) for _name in _chanda_names
                    )
                    multi_chanda[''.join(multi_lakshana)].extend(names)
                    splits[''.join(multi_lakshana)].append(multi_lakshana)


                    if len(multi_pada) == 4:
                        # also add signature for 3+4
                        names = tuple(
                            (_name, tuple(multi_pada[2:])) for _name in _chanda_names
                        )
                        multi_chanda[''.join(multi_lakshana[2:])].extend(names)
                        splits[''.join(multi_lakshana[2:])].append(multi_lakshana[2:])

                        multi_pada = []
                        multi_lakshana = []

        for k, v in chanda.items():
            self.SINGLE_CHANDA[k].extend(v)
            self.CHANDA[k].extend(v)
        for k, v in multi_chanda.items():
            self.MULTI_CHANDA[k].extend(v)
            self.CHANDA[k].extend(v)

        self.SPLITS.update(splits)
        return chanda

    # ----------------------------------------------------------------------- #

    def read_matra_definitions(self, matra_file: str) -> Dict[Tuple[int, ...], Tuple[str, ...]]:
        """
        Read definitions of mātrā-vṛtta from a CSV file.

        Parameters
        ----------
        matra_file : str
            Path to the CSV file containing mātrā-vṛtta definitions.

        Returns
        -------
        dict
            Mapping of mātrā pattern tuples to meter names.

        Notes
        -----
        The CSV is expected to have:
        - First column: name(s) of mātrā-vṛtta
        - Second column: mātrā pattern (e.g., ``"12-18-12-15"``)
        """
        matra_chanda = {}
        with open(matra_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = True
            for row in reader:
                if header:
                    header = False
                    continue
                if not row[0].strip():
                    continue

                names = tuple(c.strip() for c in row[0].split(','))
                matra_str = row[1].strip() if len(row) > 1 else ''

                if matra_str:
                    matra_pattern = tuple(
                        int(m.strip()) for m in matra_str.split('-')
                    )
                    for name in names:
                        self.MATRA_PATTERNS[name] = matra_pattern
                    meters = tuple((name, ()) for name in names)
                    self.MATRA_CHANDA[matra_pattern].extend(meters)
                    matra_chanda[matra_pattern] = names

        return matra_chanda

    # ----------------------------------------------------------------------- #

    def read_data(self) -> None:
        """
        Load all meter definitions from CSV sources.

        Returns
        -------
        None
        """
        self.read_jaati(os.path.join(self.data_path, 'chanda_jaati.csv'))
        definition_files = [
            'chanda_sama.csv', 'chanda_ardhasama.csv', 'chanda_vishama.csv'
        ]
        for chanda_file in definition_files:
            self.read_chanda_definitions(
                os.path.join(self.data_path, chanda_file)
            )
        matra_file = os.path.join(self.data_path, 'chanda_matra.csv')
        if os.path.exists(matra_file):
            self.read_matra_definitions(matra_file)

    # ----------------------------------------------------------------------- #

    def read_examples(self) -> Dict[str, Any]:
        """
        Read bundled example data.

        Returns
        -------
        dict
            Example payload loaded from ``examples.json``.
        """
        example_file = os.path.join(self.data_path, "examples.json")
        with open(example_file, "r") as f:
            examples = json.load(f)
        return examples

    ###########################################################################

    def process_text(self, text: str) -> Tuple[List[str], str]:
        """
        Process input text and detect transliteration scheme.

        Parameters
        ----------
        text : str
            Input Sanskrit text in any supported scheme.

        Returns
        -------
        list[str]
            Cleaned Devanagari lines.
        str
            Detected transliteration scheme.
        """
        return SanskritTextProcessor.process_and_detect_scheme(text)

    ###########################################################################

    @functools.lru_cache(maxsize=MAX_CACHE)
    def _editops(
        self,
        lg_str: str,
        lg_signature: str,
        replace_cost: int = 1,
        delete_cost: int = 1,
        insert_cost: int = 1,
        max_diff: int = 10
    ) -> Tuple[int, Optional[List[Tuple[str, int, int]]]]:
        """
        Compute edit operations between two laghu-guru strings.

        Parameters
        ----------
        lg_str : str
            Input laghu-guru string.
        lg_signature : str
            Target laghu-guru string.
        replace_cost : int, optional
            Cost of replace operations.
        delete_cost : int, optional
            Cost of delete operations.
        insert_cost : int, optional
            Cost of insert operations.
        max_diff : int, optional
            Maximum allowed edit operations before giving up.

        Returns
        -------
        tuple
            ``(cost, ops)`` where ``ops`` is a list of edit operations or
            ``None`` if the distance exceeds ``max_diff``.
        """
        ops = Lev.editops(lg_str, lg_signature)

        if not ops:
            return 0, []

        distance = len(ops)
        if distance > max_diff:
            return distance, None

        op_cost = {
            'replace': replace_cost,
            'delete': delete_cost,
            'insert': insert_cost
        }

        cost = sum(op_cost[op[0]] for op in ops)
        return cost, ops

    def transform(
        self,
        syllables: Syllables,
        lg_marks: List[str],
        lg_str: str,
        signature: str,
        replace_cost: int = 1,
        delete_cost: int = 1,
        insert_cost: int = 1,
        max_diff: int = 3
    ) -> Tuple[int, Optional[Syllables]]:
        """
        Find possible transformations of a source line to fit a signature.

        Parameters
        ----------
        syllables : list
            Nested syllable structure from ``mark_syllable_weights``.
        lg_marks : list[str]
            Laghu-guru marks aligned to syllables.
        lg_str : str
            Flattened laghu-guru string.
        signature : str
            Target gaṇa signature.
        replace_cost : int, optional
            Cost of replace operations.
        delete_cost : int, optional
            Cost of delete operations.
        insert_cost : int, optional
            Cost of insert operations.
        max_diff : int, optional
            Maximum allowed edit operations before giving up.

        Returns
        -------
        tuple
            ``(cost, output)`` where output is a nested syllable structure
            with edit annotations, or ``None`` if the edit distance is too high.
        """
        lg_signature = self.gana_to_lg(signature)
        cost, ops = self._editops(
            lg_str,
            lg_signature,
            replace_cost=replace_cost,
            delete_cost=delete_cost,
            insert_cost=insert_cost,
            max_diff=max_diff
        )

        if ops is None:
            return cost, None

        if not ops:
            return 0, []

        distance = len(ops)

        idx = 0  # overall index (syllables, lg_marks)
        lg_idx = 0  # index in the lg_str
        op_idx = 0  # index in the list of edit operations

        output = []

        op, spos, dpos = ops[op_idx]

        # ------------------------------------------------------------------- #
        for lid, line in enumerate(syllables):
            output_line = []
            # --------------------------------------------------------------- #
            for wid, word in enumerate(line):
                output_word = []
                # ----------------------------------------------------------- #
                for cid, syllable in enumerate(word):
                    output_syllable = syllable
                    if lg_marks[idx]:
                        if lg_idx == spos:
                            if op[0] == 'i':
                                output_syllable = f'i({lg_signature[dpos]})'
                                output_word.append(output_syllable)
                                op_idx += 1
                                # insertion means we need to continue with
                                # the same syllable but next operation,
                                # so we increment op_idx
                                # Hence the other condition (op[0] != 'i')
                                # cannot be in the 'else' part directly

                            if op_idx < distance:
                                op, spos, dpos = ops[op_idx]

                                if op[0] != 'i':
                                    output_syllable = f'{op[0]}({syllable})'
                                    if op[0] == 'r':
                                        substitute = lg_signature[dpos]
                                        output_syllable += f'[{substitute}]'
                                        laghu = skt.is_laghu(syllable)
                                        if not laghu == (substitute == self.L):
                                            tm = skt.toggle_matra(
                                                syllable
                                            )
                                            if tm:
                                                # toggle was successful
                                                output_syllable += f'{{{tm}}}'
                                op_idx += 1
                                if op_idx < distance:
                                    op, spos, dpos = ops[op_idx]

                        # increase index in Laghu-Guru string if valid mark
                        lg_idx += 1

                    # always increment syllable index
                    idx += 1
                    output_word.append(output_syllable)
                # ----------------------------------------------------------- #
                output_line.append(output_word)
            # --------------------------------------------------------------- #
            output.append(output_line)
        # ------------------------------------------------------------------- #

        return cost, output

    ###########################################################################

    def find_direct_match(self, line: str, multi: bool = False) -> Optional[Dict[str, Any]]:
        """
        Find direct chanda matches for a single line.

        Parameters
        ----------
        line : str
            Input line in Devanagari.
        multi : bool, optional
            Whether to use multi-pada dictionaries.

        Returns
        -------
        dict or None
            Match payload if available; otherwise ``None``.
        """
        scan = self._scan_line(line)
        if scan is None:
            return None
        return self._build_match(scan, multi=multi)

    ###########################################################################

    def find_matra_match(self, matra_counts: Tuple[int, ...]) -> Dict[str, Any]:
        """
        Find mātrā-vṛtta based on mātrā counts per pada.

        Parameters
        ----------
        matra_counts : tuple[int, ...]
            Mātrā counts per pada (e.g., ``(12, 18, 12, 15)``).

        Returns
        -------
        dict
            Dictionary containing match results.
        """
        found = matra_counts in self.MATRA_CHANDA

        chanda = []
        if found:
            chanda = self.MATRA_CHANDA.get(matra_counts, [])
        elif len(matra_counts) == 2:
            # Allow 2-line verses by collapsing 4-pada patterns (p1+p2, p3+p4)
            collapsed = []
            for pattern, meters in self.MATRA_CHANDA.items():
                if len(pattern) == 4:
                    if (pattern[0] + pattern[1], pattern[2] + pattern[3]) == matra_counts:
                        collapsed.extend(meters)
            if collapsed:
                found = True
                chanda = collapsed

        matra_str = '-'.join(str(m) for m in matra_counts)

        match = {
            'found': found,
            'chanda': chanda,
            'matra_pattern': matra_counts,
            'matra_display': matra_str,
            'is_matra_vrtta': True
        }
        return match

    ###########################################################################

    def analyze_text(
        self,
        text: str,
        verse: bool = False,
        fuzzy: bool = False,
        save_path: Optional[str] = None,
        scheme: Optional[str] = None,
        verse_lines: int = DEFAULT_VERSE_LINES
    ) -> TextAnalysisResult:
        """
        Identify meters from text.

        Parameters
        ----------
        text : str
            Input Sanskrit text.
        verse : bool, optional
            If ``True``, treat input as collection of verses.
        fuzzy : bool, optional
            Enable fuzzy matching.
        save_path : str, optional
            Path to save results (JSON and text files).
        scheme : str, optional
            Output transliteration scheme.
        verse_lines : int, optional
            Number of lines per verse (default: 4 for ślokas).

        Returns
        -------
        TextAnalysisResult
            Result object containing line and verse analyses.

        Notes
        -----
        Supports configurable verse line grouping; mātrā-vṛtta matching
        also allows two-line collapse of four-pāda patterns.
        """
        line_results: List[LineResult] = []
        verse_results: List[VerseResult] = []

        lines, detected_scheme = self.process_text(text)
        output_scheme = scheme or detected_scheme

        for line in lines:
            if not line:
                continue
            result = self.analyze_line(
                line,
                fuzzy=fuzzy
            )
            if output_scheme:
                if result.scheme and result.scheme != output_scheme:
                    result.line = transliterate(result.line, result.scheme, output_scheme)
                result.scheme = output_scheme
            line_results.append(LineResult(result=result, index=len(line_results)))

        if verse:
            verse_result = VerseResult()

            line_count = 0
            ongoing_score = Counter()
            verse_matra_options = []

            for line_idx, line_result in enumerate(line_results):
                result = line_result.result
                if result.matra:
                    matra_options = self._matra_options_from_result(result)
                    if matra_options:
                        verse_matra_options.append(matra_options)
                if result.found:
                    _chanda = result.chanda
                    _unique_chanda = list(dict(_chanda))
                    for _c in _unique_chanda:
                        ongoing_score[_c] += 1
                    # TODO:
                    # If the exact match is by accident, other matches don't
                    # get a score. Decide if we want to calculate fuzzy matches
                    # irrespective of an exact match or not.
                else:
                    for fuzzy_match in result.fuzzy:
                        _chanda = fuzzy_match['chanda']
                        _unique_chanda = list(dict(_chanda))
                        for _c in _unique_chanda:
                            ongoing_score[_c] += fuzzy_match['similarity']

                verse_result.line_indices.append(line_idx)
                line_count += 1
                if line_count % verse_lines == 0 or line_idx == len(line_results) - 1:
                    if len(verse_matra_options) >= 2:
                        for matra_tuple in self._iter_matra_tuples(verse_matra_options):
                            matra_match = self.find_matra_match(matra_tuple)
                            if matra_match['found']:
                                for name, pada in matra_match['chanda']:
                                    ongoing_score[name] += len(verse_result.line_indices)
                                break

                    verse_scores = ongoing_score.most_common()
                    if verse_scores:
                        best_score = verse_scores[0][1]
                        best_matches = ([
                            _c
                            for _c, _score in verse_scores
                            if _score == best_score
                        ], best_score)
                        verse_result.scores = verse_scores
                        verse_result.chanda = best_matches
                        for _line_idx in verse_result.line_indices:
                            line_result = line_results[_line_idx]
                            priority_fuzzy = []
                            remaining_fuzzy = []
                            existing_fuzzy = list(line_result.result.fuzzy)
                            for fuzzy_match in existing_fuzzy:
                                if any(
                                    (x in best_matches[0])
                                    for x in [c[0] for c in fuzzy_match['chanda']]
                                ):
                                    priority_fuzzy.append(fuzzy_match)
                                else:
                                    remaining_fuzzy.append(fuzzy_match)
                            line_result.result.fuzzy = priority_fuzzy + remaining_fuzzy

                    verse_result.line_results = [
                        line_results[i] for i in verse_result.line_indices
                    ]
                    verse_results.append(verse_result)
                    # reset
                    verse_result = VerseResult()
                    ongoing_score = Counter()
                    verse_matra_options = []

        analysis = AnalysisResult(
            scheme=output_scheme,
            line=line_results,
            verse=verse_results
        )

        simple_result = []
        if verse:
            for verse_result in verse_results:
                if verse_result.chanda:
                    best_matches = " / ".join(verse_result.chanda[0])
                    best_score = verse_result.chanda[1]
                    simple_result.append(f"# {best_matches} ({best_score})")
                    simple_result.append("")
                for line_id in verse_result.line_indices:
                    line_result = line_results[line_id]
                    simple_result.append(
                        self.format_line_result(line_result.result)
                    )
                simple_result.append("")
        else:
            for line_result in line_results:
                simple_result.append(
                    self.format_line_result(line_result.result)
                )
                simple_result.append("")

        if save_path is not None:
            os.makedirs(save_path, exist_ok=True)

            md5sum = hashlib.md5(text.encode('utf-8')).hexdigest()
            result_id = f"result_{md5sum}_{int(verse)}_{int(fuzzy)}"

            json_filename = f"{result_id}.json"
            json_path = os.path.join(save_path, json_filename)
            with open(json_path, mode="w", encoding="utf-8") as f:
                json.dump(analysis.to_dict(), f, ensure_ascii=False)

            txt_filename = f"{result_id}.txt"
            txt_path = os.path.join(save_path, txt_filename)
            with open(txt_path, mode="w", encoding="utf-8") as f:
                f.write("\n".join(simple_result))
        else:
            md5sum = None
            json_filename = None
            txt_filename = None

        paths = {
            'json': json_filename,
            'txt': txt_filename
        }
        return TextAnalysisResult(result=analysis, path=paths)

    # ----------------------------------------------------------------------- #

    def _collect_matches(
        self,
        direct_match: Dict[str, Any],
        multi_match: Dict[str, Any],
        regex_matches: List[str]
    ) -> Dict[str, List]:
        """
        Collect all matching chanda information from different match types.

        Parameters
        ----------
        direct_match : dict
            Direct pattern match results.
        multi_match : dict
            Multi-pada match results.
        regex_matches : list[str]
            Regex pattern matches.

        Returns
        -------
        dict
            Collected ``chanda``, ``jaati``, ``gana``, ``length``, ``matra`` lists.
        """
        result = {
            'chanda': [],
            'jaati': [],
            'gana': [],
            'length': [],
            'matra': []
        }

        if direct_match['found']:
            result['chanda'] += direct_match['chanda']
            result['jaati'] += direct_match['jaati']
            result['gana'] += direct_match['gana']
            result['length'] += direct_match['length']
            result['matra'] += direct_match['matra']

        if multi_match['found']:
            result['chanda'] += multi_match['chanda']
            result['jaati'] += multi_match['jaati']
            result['gana'] += multi_match['gana']
            result['length'] += multi_match['length']
            result['matra'] += multi_match['matra']

        if regex_matches:
            result['chanda'] += [
                c
                for m in regex_matches
                for c in self.CHANDA.get(m)
                if c not in result['chanda']
            ]

        return result

    def _compute_fuzzy_matches(
        self,
        scan: Dict[str, Any],
        k: int,
        max_diff: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Compute fuzzy matches for a line that didn't have an exact match.

        Parameters
        ----------
        scan : dict
            Scanned line payload from ``_scan_line``.
        k : int
            Maximum number of fuzzy matches to return.
        max_diff : int, optional
            Maximum edit distance to consider.

        Returns
        -------
        list[dict]
            Fuzzy match dictionaries sorted by similarity.
        """
        fuzzy_matches = []

        lg_str = scan['lg_str']
        for chanda_lg, chanda_names in self.CHANDA.items():
            if abs(len(chanda_lg) - len(lg_str)) > max_diff:
                continue
            chanda_gana = self.lg_to_gana(chanda_lg)
            cost, suggestion = self.transform(
                syllables=scan['syllables_nested'],
                lg_marks=scan['lg_marks'],
                lg_str=lg_str,
                signature=chanda_lg,
                max_diff=max_diff,
            )

            if len(chanda_lg) > 0:
                similarity = (1 - cost / len(chanda_lg))
            else:
                similarity = 0

            if suggestion:
                fuzzy_matches.append({
                    "chanda": chanda_names,
                    "gana": chanda_gana.translate(self.ttable_out),
                    "suggestion": suggestion,
                    "cost": cost,
                    "similarity": similarity,
                })

        return sorted(fuzzy_matches, key=lambda x: x["similarity"], reverse=True)[:k]

    def analyze_line(
        self,
        line: str,
        fuzzy: bool = False,
        k: int = 10
    ) -> ChandaResult:
        """
        Identify chanda from a single text line.

        Parameters
        ----------
        line : str
            Input text line.
        fuzzy : bool, optional
            Enable fuzzy matching.
        k : int, optional
            Maximum number of fuzzy matches to return.

        Returns
        -------
        ChandaResult
            Result containing identification details and optional fuzzy matches.
        """
        lines, scheme = self.process_text(line)
        output_line = line

        if len(lines) > 1:
            raise ValueError('Input contains more than one line.')

        if not lines or len(lines) == 0:
            empty = self._empty_result(output_line, scheme)
            return ChandaResult.from_dict(empty)

        line = lines[0]
        output_line = (
            transliterate(line, sanscript.DEVANAGARI, scheme)
            if scheme and scheme != sanscript.DEVANAGARI else line
        )

        scan = self._scan_line(line, clean=False)
        if scan is None:
            empty = self._empty_result(output_line, scheme)
            return ChandaResult.from_dict(empty)

        # Get matches using a single scan
        direct_match = self._build_match(scan, multi=False)
        multi_match = self._build_match(scan, multi=True)

        # Check for pattern matches
        lg_str = scan['lg_str']
        lg_candidates = [lg_str]
        if lg_str.endswith(self.L):
            lg_candidates.append(lg_str[:-1] + self.G)
        regex_matches = [
            pattern
            for pattern in self.CHANDA
            if any(re.match(f'^{pattern}$', candidate) for candidate in lg_candidates)
        ]

        found = direct_match['found'] or multi_match['found'] or bool(regex_matches)

        # Collect all matches
        matches = self._collect_matches(direct_match, multi_match, regex_matches) if found else {
            'chanda': [], 'jaati': [], 'gana': [], 'length': [], 'matra': []
        }

        # Compute full properties
        full_lg = [self.output_map.get(c, c) for c in scan['lg_marks']]
        full_length = len(lg_str)
        full_matra = self.count_matra(lg_str)
        full_gana = self.lg_to_gana(lg_str).translate(self.ttable_out)
        full_jaati = self.JAATI.get(len(lg_str), self.JAATI[-1])
        jaati = matches['jaati'] if matches['jaati'] else list(full_jaati)

        # Build result
        answer = {
            'found': found,
            'line': output_line,
            'scheme': scheme,
            'syllables': direct_match['syllables'],
            'lg': full_lg,
            'gana': full_gana,
            'length': full_length,
            'matra': full_matra,
            'chanda': matches['chanda'],
            'jaati': jaati
        }

        # Add fuzzy matches if needed
        answer['fuzzy'] = (
            self._compute_fuzzy_matches(scan, k)
            if not found and fuzzy else []
        )

        return ChandaResult.from_dict(answer)

    ###########################################################################

    @classmethod
    def summarize_results(
        cls,
        results: Union[TextAnalysisResult, AnalysisResult, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Summarize line and verse match statistics.

        Parameters
        ----------
        results : TextAnalysisResult or AnalysisResult or dict
            Analysis results to summarize.

        Returns
        -------
        dict
            Summary statistics for line and verse matches.
        """
        if isinstance(results, TextAnalysisResult):
            results = results.result
        if isinstance(results, AnalysisResult):
            results = results.to_dict()

        line_results = results.get('line', [])
        verse_results = results.get('verse', [])

        match_line_statistics = defaultdict(Counter)
        fuzzy_line_statistics = defaultdict(Counter)
        verse_statistics = defaultdict(Counter)

        counts = defaultdict(int)

        for line_answer in line_results:
            counts['line'] += 1
            line_result = line_answer.get('result', line_answer)
            if line_result['found']:
                counts['match_line'] += 1
                chanda_list = [
                    cls.format_chanda_pada(c, p)
                    for c, p in line_result.get('chanda', [])
                ]
                gana_list = [line_result.get('gana', "")]

                match_line_statistics['chanda'].update(chanda_list)
                match_line_statistics['gana'].update(gana_list)
            else:
                counts['fuzzy_line'] += 1
                for idx, fuzzy_match in enumerate(line_result['fuzzy']):
                    if idx == 0:
                        counts['mismatch_syllable'] += fuzzy_match['cost']
                    chanda_list = cls.format_chanda_list(
                        fuzzy_match.get('chanda', [])
                    ).split('/') if fuzzy_match.get('chanda') else []
                    fuzzy_line_statistics['chanda'].update(chanda_list)
                    break

        for verse_result in verse_results:
            counts['verse'] += 1
            if not verse_result.get('chanda'):
                counts['fuzzy_verse'] += 1
                continue
            chanda_list, chanda_score = verse_result['chanda']
            verse_len = len(verse_result.get('line_indices', []))
            if not verse_len and verse_result.get('line_results'):
                verse_len = len(verse_result['line_results'])
            if chanda_score == verse_len:
                counts['match_verse'] += 1
            else:
                counts['fuzzy_verse'] += 1
            verse_statistics['chanda'].update(chanda_list)

        return {
            'verse': verse_statistics,
            'line': {
                'fuzzy': fuzzy_line_statistics,
                'match': match_line_statistics,
            },
            'count': counts
        }

    ###########################################################################
    # Formatters

    @staticmethod
    def format_chanda_pada(chanda: str, pada: tuple) -> str:
        return _format_chanda_pada(chanda, pada)

    @staticmethod
    def format_chanda_list(chanda_list: List[Tuple[str, Tuple]]) -> str:
        return _format_chanda_list(chanda_list)

    @staticmethod
    def format_line_result(line_result) -> str:
        return _format_line_result(line_result)

    @staticmethod
    def format_summary(result_summary) -> str:
        return _format_summary(result_summary)

    ###########################################################################


def analyze_line(
    text: str,
    fuzzy: bool = True,
    k: int = 10,
    output_scheme: Optional[str] = None,
    data_path: Optional[str] = None,
    language: str = 'sanskrit'
) -> ChandaResult:
    """
    Identify meter from a single line of Sanskrit text.

    Parameters
    ----------
    text : str
        Sanskrit text (single line) in any supported script.
    fuzzy : bool, optional
        Enable fuzzy matching if exact match not found.
    k : int, optional
        Maximum number of fuzzy matches to return.
    output_scheme : str, optional
        Transliteration scheme for output (e.g., ``'iast'``, ``'itrans'``).
    data_path : str, optional
        Path to meter definition data directory. If ``None``, uses package default.
    language : str, optional
        Language for prosody analysis (``'sanskrit'``, ``'vedic'``, ``'prakrit'``).

    Returns
    -------
    ChandaResult
        Identification result for the line.

    Raises
    ------
    ValueError
        If text contains more than one line.

    Examples
    --------
    >>> result = analyze_line("को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्")
    >>> print([name for name, _ in result.chanda])
    ['अनुष्टुभ्']
    >>> print(result.gana)
    'मरतयजग'
    >>> print(result.matra)
    32
    """
    if data_path is None:
        from .utils import get_default_data_path
        data_path = get_default_data_path()

    analyzer = Chanda(data_path, language=language)
    result = analyzer.analyze_line(
        text,
        fuzzy=fuzzy,
        k=k
    )

    if output_scheme:
        if result.scheme:
            result.line = transliterate(result.line, result.scheme, output_scheme)
        result.scheme = output_scheme

    return result


def analyze_text(
    text: str,
    verse_mode: bool = False,
    fuzzy: bool = True,
    output_scheme: Optional[str] = None,
    data_path: Optional[str] = None,
    language: str = 'sanskrit'
) -> TextAnalysisResult:
    """
    Identify meters for multi-line Sanskrit text.

    Parameters
    ----------
    text : str
        Sanskrit text (can be multiple lines).
    verse_mode : bool, optional
        If ``True``, group lines into 4-line verses.
    fuzzy : bool, optional
        Enable fuzzy matching.
    output_scheme : str, optional
        Transliteration scheme for output.
    data_path : str, optional
        Path to meter definition data directory.
    language : str, optional
        Language for prosody analysis (``'sanskrit'``, ``'vedic'``, ``'prakrit'``).

    Returns
    -------
    TextAnalysisResult
        Analysis results with line and verse results.

    Examples
    --------
    >>> text = '''को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्।
    ... धर्मज्ञश्च कृतज्ञश्च सत्यवाक्यो दृढव्रतः॥'''
    >>> results = analyze_text(text, verse_mode=True)
    >>> for line in results.result.line:
    ...     print([name for name, _ in line.result.chanda])
    """
    if data_path is None:
        from .utils import get_default_data_path
        data_path = get_default_data_path()

    analyzer = Chanda(data_path, language=language)
    results = analyzer.analyze_text(
        text,
        verse=verse_mode,
        fuzzy=fuzzy,
        scheme=output_scheme
    )

    return results


###############################################################################
