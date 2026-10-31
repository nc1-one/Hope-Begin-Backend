"""
Daily Hope: one email a day for 21 days, in every language the site
speaks. Each language module (en.py, tl.py, fr.py, de.py, es.py, ko.py) has
DAYS, a dict from day number to:

    title     a few words, no colon
    opening   the first part, before the verse
    verse     the verse text, copied exactly from the language's
              public-domain Protestant edition (see below)
    verse_ref the reference as that edition's readers write it
    after     the part after the verse
    question  one question to think about today
    prayer    a short prayer, to God through Jesus

Text is plain. A blank line (\\n\\n) starts a new paragraph; there are no
line breaks inside a paragraph.

Editions: World English Bible (en), Ang Dating Biblia 1905 (tl), Louis
Segond 1910 (fr), Luther 1912 (de), Reina-Valera 1909 (es), 개역한글 (ko).
Never retype a verse from memory.

Each language writes the day in its own words around the same theme and
verse; it is not a word-for-word translation of the English.
"""

from importlib import import_module

LANGUAGES = ('en', 'tl', 'fr', 'de', 'es', 'ko')
LAST_DAY = 21
FIELDS = ('title', 'opening', 'verse', 'verse_ref', 'after', 'question', 'prayer')

# The verse and theme of each day, the same in every language.
PLAN = {
    1: ('Romans 15:13', 'Hope Begins Here'),
    2: ('Ecclesiastes 3:11', 'You’re Not Behind'),
    3: ('Matthew 11:28', 'When You’re Tired'),
    4: ('Philippians 4:6-7', 'Peace in the Chaos'),
    5: ('Psalm 139:14', 'You Are Enough in Him'),
    6: ('Proverbs 3:5-6', 'When You Feel Lost'),
    7: ('Lamentations 3:22-23', 'You Made It'),
    8: ('James 1:4', 'When You Feel Stuck'),
    9: ('1 John 1:9', 'When You Feel Guilty'),
    10: ('Psalm 34:18', 'When You Feel Alone'),
    11: ('Galatians 6:9', 'When You Feel Like Giving Up'),
    12: ('Colossians 3:13', 'Learning to Forgive'),
    13: ('Zechariah 4:10', 'Small Wins Matter'),
    14: ('Isaiah 43:19', 'A New Beginning Again'),
    15: ('Ephesians 2:10', 'You Have a Purpose'),
    16: ('1 Peter 2:9', 'You Are Chosen'),
    17: ('Philippians 4:13', 'You Are Being Strengthened'),
    18: ('Romans 8:28', 'Your Story Matters'),
    19: ('Galatians 6:2', 'You Are Not Alone in the Fight'),
    20: ('Philippians 1:6', 'God Is Still Working'),
    21: ('2 Corinthians 3:18', 'You Are Becoming'),
}

# Calm daylight photos, the same in every language.
IMAGES = {
    1: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?auto=format&fit=crop&q=80&w=800',
    2: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&q=80&w=800',
    3: 'https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?auto=format&fit=crop&q=80&w=800',
    4: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=800',
    5: 'https://images.unsplash.com/photo-1493246507139-91e8fad9978e?auto=format&fit=crop&q=80&w=800',
    6: 'https://images.unsplash.com/photo-1499346030926-9a72daac6c63?auto=format&fit=crop&q=80&w=800',
    7: 'https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?auto=format&fit=crop&q=80&w=800',
    8: 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&q=80&w=800',
    9: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&q=80&w=800',
    10: 'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&q=80&w=800',
    11: 'https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&q=80&w=800',
    12: 'https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?auto=format&fit=crop&q=80&w=800',
    13: 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&q=80&w=800',
    14: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&q=80&w=800',
    15: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?auto=format&fit=crop&q=80&w=800',
    16: 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&q=80&w=800',
    17: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&q=80&w=800',
    18: 'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&q=80&w=800',
    19: 'https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&q=80&w=800',
    20: 'https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?auto=format&fit=crop&q=80&w=800',
    21: 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&q=80&w=800',
}


def day_in(lang, day):
    """The day's words in a language, else in English; None past the last day."""
    if not 1 <= day <= LAST_DAY:
        return None
    module = import_module(f'{__name__}.{lang if lang in LANGUAGES else "en"}')
    return module.DAYS.get(day) or import_module(f'{__name__}.en').DAYS.get(day)
