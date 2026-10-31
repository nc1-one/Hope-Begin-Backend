"""
The crisis line for each country the site covers, for emails. A copy of
the first crisis line per country in the site's src/lib/helplines.ts, where
each number is checked against the ministry's or the service's own page.
Change both together.

Anyone elsewhere gets the line of their page language's usual country
(LANGUAGE_COUNTRY), as on the site.
"""

from dataclasses import dataclass

HELPLINES_CHECKED = '2026-10-31'
FIND_A_HELPLINE = 'https://findahelpline.com'


@dataclass(frozen=True)
class Line:
    name: str
    # (as written, for tel: links)
    numbers: tuple
    all_day: bool


@dataclass(frozen=True)
class CountryHelp:
    emergency: str
    # The line's own name, as the service writes it.
    name: str
    # (as written, for tel: links); a second number is another way to call
    # the same line.
    numbers: tuple
    all_day: bool
    # The country's other line, such as a mental health line.
    second: Line | None = None


COUNTRY_HELP = {
    "PH": CountryHelp(
        emergency="911",
        name="NCMH Crisis Hotline",
        numbers=(("1553", "1553"), ("0917 899 8727", "+639178998727"),),
        all_day=True,
    ),
    "US": CountryHelp(
        emergency="911",
        name="988 Suicide & Crisis Lifeline",
        numbers=(("988", "988"),),
        all_day=True,
    ),
    "CA": CountryHelp(
        emergency="911",
        name="9-8-8: Suicide Crisis Helpline",
        numbers=(("988", "988"),),
        all_day=True,
    ),
    "GB": CountryHelp(
        emergency="999",
        name="Samaritans",
        numbers=(("116 123", "116123"),),
        all_day=True,
    ),
    "IE": CountryHelp(
        emergency="112",
        name="Pieta 24-Hour Crisis Helpline",
        numbers=(("1800 247 247", "+3531800247247"),),
        all_day=True,
        second=Line("Samaritans", (("116 123", "116123"),), True),
    ),
    "AU": CountryHelp(
        emergency="000",
        name="Lifeline",
        numbers=(("13 11 14", "131114"),),
        all_day=True,
    ),
    "NZ": CountryHelp(
        emergency="111",
        name="1737, Need to talk?",
        numbers=(("1737", "1737"),),
        all_day=True,
        second=Line("Depression Helpline", (("0800 111 757", "+64800111757"),), True),
    ),
    "SG": CountryHelp(
        emergency="995",
        name="Samaritans of Singapore (SOS)",
        numbers=(("1767", "1767"),),
        all_day=True,
    ),
    "FR": CountryHelp(
        emergency="112",
        name="Numéro national de prévention du suicide",
        numbers=(("3114", "3114"),),
        all_day=True,
    ),
    "BE": CountryHelp(
        emergency="112",
        name="Centre de Prévention du Suicide",
        numbers=(("0800 32 123", "+3280032123"),),
        all_day=True,
        second=Line("Télé-Accueil", (("107", "107"),), True),
    ),
    "CH": CountryHelp(
        emergency="144",
        name="La Main Tendue / Die Dargebotene Hand",
        numbers=(("143", "143"),),
        all_day=True,
    ),
    "LU": CountryHelp(
        emergency="112",
        name="SOS Détresse",
        numbers=(("45 45 45", "+352454545"),),
        all_day=False,
    ),
    "DE": CountryHelp(
        emergency="112",
        name="TelefonSeelsorge",
        numbers=(("0800 111 0 111", "+498001110111"), ("0800 111 0 222", "+498001110222"),),
        all_day=True,
    ),
    "AT": CountryHelp(
        emergency="144",
        name="Telefonseelsorge, Notruf 142",
        numbers=(("142", "142"),),
        all_day=True,
        second=Line("Ö3-Kummernummer", (("116 123", "116123"),), False),
    ),
    "MX": CountryHelp(
        emergency="911",
        name="Línea de la Vida",
        numbers=(("800 911 2000", "+528009112000"),),
        all_day=True,
    ),
    "CO": CountryHelp(
        emergency="123",
        name="Línea 106",
        numbers=(("106", "106"),),
        all_day=True,
    ),
    "AR": CountryHelp(
        emergency="911",
        name="Línea Nacional de Orientación y Apoyo en la Urgencia de Salud Mental",
        numbers=(("0800 999 0091", "+548009990091"),),
        all_day=True,
    ),
    "CL": CountryHelp(
        emergency="131",
        name="Línea de Prevención del Suicidio *4141",
        numbers=(("*4141", "*4141"),),
        all_day=True,
    ),
    "PE": CountryHelp(
        emergency="106",
        name="Línea 113 Salud, opción 5 (salud mental)",
        numbers=(("113", "113"),),
        all_day=True,
    ),
    "EC": CountryHelp(
        emergency="911",
        name="Línea 171, opción 6 (salud mental)",
        numbers=(("171", "171"),),
        all_day=False,
    ),
    "ES": CountryHelp(
        emergency="112",
        name="024. Línea de atención a la conducta suicida",
        numbers=(("024", "024"),),
        all_day=True,
    ),
    "KR": CountryHelp(
        emergency="119",
        name="자살예방상담전화",
        numbers=(("109", "109"),),
        all_day=True,
        second=Line("정신건강위기상담전화", (("1577-0199", "15770199"),), True),
    ),
}

# Whose line to show when the visitor's phone didn't say where it is.
LANGUAGE_COUNTRY = {
    'en': 'PH',
    'tl': 'PH',
    'fr': 'FR',
    'de': 'DE',
    'es': 'MX',
    'ko': 'KR',
}


def help_for(country, lang):
    """
    The line for where the visitor is: the country code from their phone,
    when the site has lines for it. Otherwise (no code, or a country the site
    has no lines for), the page language's usual country, so every email
    names a line. A Korean reader in Manila gets the Philippines' line, an
    English reader in Seoul gets Korea's.
    """
    return COUNTRY_HELP.get((country or '').upper()) or COUNTRY_HELP[LANGUAGE_COUNTRY.get(lang, 'PH')]
