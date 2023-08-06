__title__ = 'transliterate.__init__'
__version__ = '0.6'
__build__ = 0x000006
__author__ = 'Artur Barseghyan'
__all__ = ('autodiscover',)

import os

try:
    from importlib import import_module
except ImportError:
    import_module = __import__

from transliterate.helpers import PROJECT_DIR
from transliterate.conf import get_setting

def autodiscover():
    """
    Autodiscovers the language packs in contrib/apps.
    """
    LANGUAGES_DIR = get_setting('LANGUAGES_DIR')
    LANGUAGE_PACK_MODULE_NAME = get_setting('LANGUAGE_PACK_MODULE_NAME')
    DEBUG = get_setting('DEBUG')

    for app_path in os.listdir(PROJECT_DIR(LANGUAGES_DIR)):
        full_app_path = list(LANGUAGES_DIR)
        full_app_path.append(app_path)
        if os.path.isdir(PROJECT_DIR(full_app_path)):
            try:
                import_module(
                    "transliterate.%s.%s.%s" % ('.'.join(LANGUAGES_DIR), app_path, LANGUAGE_PACK_MODULE_NAME)
                    )
            except ImportError, e:
                if DEBUG: print e
            except Exception, e:
                if DEBUG: print e
        else:
            pass
