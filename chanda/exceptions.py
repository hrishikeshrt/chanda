"""
Custom exceptions for the Chandojñānam library.

This module defines domain-specific exceptions raised by the API.
"""


class ChandaError(Exception):
    """
    Base exception for all Chandojñānam errors.
    """
    pass


class InvalidInputError(ChandaError):
    """
    Raised when input text is invalid or cannot be processed.
    """
    pass


class MeterNotFoundError(ChandaError):
    """
    Raised when no meter match is found and fuzzy matching is disabled.
    """
    pass


class DataFileError(ChandaError):
    """
    Raised when meter definition data files cannot be loaded.
    """
    pass


class ScriptDetectionError(ChandaError):
    """
    Raised when the input script cannot be detected.
    """
    pass
