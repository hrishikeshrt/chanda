"""
Utility functions for the Chandojñānam library.

This module provides small helpers for locating data files and
reporting supported meter counts.
"""

import os
import csv
from typing import Optional, Set

from .types import MeterStats


def get_default_data_path() -> str:
    """
    Get the default path to meter definition data files.

    Returns
    -------
    str
        Absolute path to the packaged data directory.
    """
    return os.path.join(os.path.dirname(__file__), 'data')


def get_supported_meters(data_path: Optional[str] = None) -> MeterStats:
    """
    Get statistics about supported meters in the database.

    Parameters
    ----------
    data_path : str, optional
        Path to meter definition data directory. If ``None``, uses the
        package default.

    Returns
    -------
    MeterStats
        Counts of different meter types and total unique meters.

    Examples
    --------
    >>> meters = get_supported_meters()
    >>> print(f"Total meters: {meters.total}")
    >>> print(f"Sama meters: {meters.sama}")
    >>> print(f"Ardhasama meters: {meters.ardhasama}")
    >>> print(f"Vishama meters: {meters.vishama}")
    >>> meter_dict = meters.to_dict()
    """
    if data_path is None:
        data_path = get_default_data_path()

    def _read_meter_names(filename: str) -> Set[str]:
        """
        Read meter names from a CSV definition file.

        Parameters
        ----------
        filename : str
            CSV path containing meter definitions.

        Returns
        -------
        set[str]
            Unique meter names found in the file.
        """
        names = set()
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = True
            for row in reader:
                if header:
                    header = False
                    continue
                if not row:
                    continue
                for name in row[0].split(','):
                    name = name.strip()
                    if name:
                        names.add(name)
        return names

    sama_meters = _read_meter_names(os.path.join(data_path, 'chanda_sama.csv'))
    ardhasama_meters = _read_meter_names(os.path.join(data_path, 'chanda_ardhasama.csv'))
    vishama_meters = _read_meter_names(os.path.join(data_path, 'chanda_vishama.csv'))
    matra_meters = _read_meter_names(os.path.join(data_path, 'chanda_matra.csv'))

    all_meters = set().union(
        sama_meters,
        ardhasama_meters,
        vishama_meters,
        matra_meters
    )

    return MeterStats(
        total=len(all_meters),
        sama=len(sama_meters),
        ardhasama=len(ardhasama_meters),
        vishama=len(vishama_meters),
        matra=len(matra_meters)
    )
