"""
Words for the emails, one module per language the site speaks. Every
module has the same keys as en.py; tests check that none is missing.

Tone: warm and informal (tu, du, tú, 해요체), like the site. Bible text
only from the public-domain Protestant editions the site uses.
"""

from importlib import import_module

LANGUAGES = ('en', 'tl', 'fr', 'de', 'es', 'ko')

# Languages whose readers are offered the Himala Everyday e-coach, who
# speaks English and Filipino. The others get their country's free lines.
ECOACH_LANGUAGES = ('en', 'tl')

# The site's address for each language's pages.
SITE_PREFIX = {'en': '', 'tl': '', 'fr': '/fr', 'de': '/de', 'es': '/es', 'ko': '/ko'}


def copy_for(lang):
    """The module for a language; English for anything unknown."""
    return import_module(f'{__name__}.{lang if lang in LANGUAGES else "en"}')


def site_path(lang, path):
    """'/action-plan' in French is '/fr/action-plan'."""
    prefix = SITE_PREFIX.get(lang, '')
    if path == '/':
        return prefix or '/'
    return prefix + path


def colon(lang):
    """': ' between a label and what follows; French puts a no-break space before it."""
    return '\u00a0: ' if lang == 'fr' else ': '
