__title__ = 'transliterate.exceptions'
__version__ = '1.0'
__build__ = 0x000010
__author__ = 'Artur Barseghyan'
__all__ = ('LanguageCodeError', 'ImproperlyConfigured', 'LanguagePackNotFound', 'LanguageDetectionError')

class LanguageCodeError(Exception):
    """
    Exception raised when language code is left empty or has incorrect value.
    """

class ImproperlyConfigured(Exception):
    """
    Exception raised when developer didn't configure the code properly.
    """

class LanguagePackNotFound(Exception):
    """
    Exception raised when language pack is not found for the language code given.
    """

class LanguageDetectionError(Exception):
    """
    Exception raised when language can't be detected for the text given.
    """
