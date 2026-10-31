"""Pieces every HopeBegins email shares: the page, buttons and the crisis line."""

from html import escape

from common.email_copy import copy_for
from common.helplines import FIND_A_HELPLINE, help_for

BROWN = '#6E5F47'
SAGE = '#AEC488'
SAGE_LIGHT = '#EFF3E7'
TEAL = '#91AFAA'
BORDER = '#ece9dd'

HTML_LANG = {'en': 'en', 'tl': 'tl', 'fr': 'fr', 'de': 'de', 'es': 'es-419', 'ko': 'ko'}


def _crisis_line(lang, country):
    c = copy_for(lang).PLAN
    return c, help_for(country, lang)


def crisis_text(lang, country=None):
    c, line = _crisis_line(lang, country)
    if line is None:
        return f"{c['crisis_title']} {c['crisis_nowhere']} {FIND_A_HELPLINE}. {c['crisis_nowhere_danger']}"
    calls = ' '.join(
        c['crisis_call_all_day' if each.all_day else 'crisis_call'].format(
            name=each.name,
            numbers=f" {c['crisis_or']} ".join(number for number, _ in each.numbers),
        )
        for each in (line, line.second)
        if each
    )
    return f"{c['crisis_title']} {calls} {c['crisis_danger'].format(emergency=line.emergency)}"


def crisis_html(lang, country=None):
    c, line = _crisis_line(lang, country)
    if line is None:
        body = (
            f"{escape(c['crisis_nowhere'])} "
            f'<a href="{FIND_A_HELPLINE}" style="color: {BROWN}; font-weight: 700;">findahelpline.com</a>. '
            f"{escape(c['crisis_nowhere_danger'])}"
        )
    else:
        # Each number is a link that dials it.
        def call(each):
            numbers = f" {escape(c['crisis_or'])} ".join(
                f'<a href="tel:{tel}" style="color: {BROWN}; font-weight: 700;">{escape(number)}</a>'
                for number, tel in each.numbers
            )
            return escape(c['crisis_call_all_day' if each.all_day else 'crisis_call']).format(
                name=escape(each.name), numbers=numbers
            )

        calls = ' '.join(call(each) for each in (line, line.second) if each)
        body = f"{calls} {escape(c['crisis_danger'].format(emergency=line.emergency))}"
    return f"""
        <div style="margin-top: 36px; border-left: 4px solid {SAGE}; padding: 4px 0 4px 16px;">
            <p style="margin: 0; font-weight: 700;">{escape(c['crisis_title'])}</p>
            <p style="margin: 4px 0 0;">{body}</p>
        </div>
    """


def button_html(url, label, or_open_link):
    return f"""
        <div style="margin: 32px 0; text-align: center;">
            <a href="{escape(url, quote=True)}" style="display: inline-block; background-color: {BROWN}; color: #ffffff; padding: 14px 24px; border-radius: 12px; text-decoration: none; font-weight: 700;">{escape(label)}</a>
            <p style="margin: 12px 0 0; font-size: 13px;">{escape(or_open_link)} <a href="{escape(url, quote=True)}" style="color: {BROWN};">{escape(url)}</a></p>
        </div>
    """


def page_html(body, lang):
    return f"""
    <html lang="{HTML_LANG.get(lang, 'en')}">
        <body style="margin: 0; padding: 24px; background-color: #fcfdfa; font-family: Arial, Helvetica, sans-serif; color: {BROWN}; line-height: 1.6;">
            <div style="max-width: 640px; margin: 0 auto; background-color: #ffffff; border-radius: 18px; padding: 32px; border: 1px solid {BORDER};">
                {body}
            </div>
        </body>
    </html>
    """
