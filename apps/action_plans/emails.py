from html import escape

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from common.email_copy import ECOACH_LANGUAGES, LANGUAGES, colon, copy_for, site_path
from common.email_parts import (
    BORDER,
    BROWN,
    SAGE_LIGHT,
    TEAL,
    button_html,
    crisis_html,
    crisis_text,
    page_html,
)
from common.utils import get_site_url

# May Himala Every Day's Facebook page. m.me opens the Messenger app on a
# phone; on a computer it stops at a messenger.com login, so the email also
# links to the page's chat on facebook.com.
ECOACH_PAGE_ID = '352008124672499'
ECOACH_APP_URL = f'https://m.me/{ECOACH_PAGE_ID}'
ECOACH_WEB_URL = f'https://www.facebook.com/messages/t/{ECOACH_PAGE_ID}'

__all__ = ['LANGUAGES', 'crisis_text', 'send_action_plan_email', 'send_check_in_email']


def _copy(lang):
    return copy_for(lang).PLAN


def _greeting(first_name, lang):
    c = _copy(lang)
    return c['greeting'].format(name=first_name) if first_name else c['greeting_no_name']


def _ordered_sections(sections, lang):
    """The safety plan always comes first."""
    heading = _copy(lang)['safety_heading']
    safety = [s for s in sections if s['heading'] == heading]
    rest = [s for s in sections if s['heading'] != heading]
    return safety + rest


def _absolute(link):
    """Site paths ("/hope-ai") become full links to the configured site."""
    return get_site_url(link) if link.startswith('/') else link


def _item_html(item):
    steps = item.get('steps') or []
    steps_html = ''
    if steps:
        steps_html = '<ol style="margin: 12px 0 0; padding-left: 20px;">' + ''.join(
            f'<li style="margin-bottom: 6px;">{escape(step)}</li>' for step in steps
        ) + '</ol>'
    link_html = ''
    if item.get('link'):
        link_html = (
            f'<p style="margin: 12px 0 0;"><a href="{escape(_absolute(item["link"]), quote=True)}" '
            f'style="color: {BROWN}; font-weight: 700;">{escape(item.get("link_label") or item["link"])}</a></p>'
        )
    detail = f'<p style="margin: 6px 0 0;">{escape(item["detail"])}</p>' if item['detail'] else ''
    return f"""
        <div style="border: 1px solid {BORDER}; border-radius: 14px; padding: 18px 20px; margin-top: 12px;">
            <p style="margin: 0; font-weight: 700; font-size: 16px;">{escape(item['title'])}</p>
            {detail}
            {steps_html}
            {link_html}
        </div>
    """


def _section_html(section):
    intro = (
        f'<p style="margin: 6px 0 0;">{escape(section["intro"])}</p>'
        if section.get('intro')
        else ''
    )
    items = ''.join(_item_html(item) for item in section['items'])
    return f"""
        <div style="margin-top: 36px;">
            <h2 style="font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 26px; margin: 0;">{escape(section['heading'])}</h2>
            {intro}
            {items}
        </div>
    """


def _someone_html(lang):
    """Someone to talk to: the e-coach in English and Taglish, else the help page."""
    c = _copy(lang)
    box = f'margin-top: 32px; background-color: {BROWN}; color: #ffffff; border-radius: 16px; padding: 24px;'
    button = f'display: inline-block; background-color: #ffffff; color: {BROWN}; padding: 12px 20px; border-radius: 12px; text-decoration: none; font-weight: 700;'
    if lang not in ECOACH_LANGUAGES:
        help_url = get_site_url(site_path(lang, '/help'))
        return f"""
        <div style="{box}">
            <p style="margin: 0; font-weight: 700; font-size: 18px;">{escape(c['help_title'])}</p>
            <p style="margin: 8px 0 16px; color: #f3f1ec;">{escape(c['help_text'])}</p>
            <a href="{help_url}" style="{button}">{escape(c['help_button'])}</a>
        </div>
    """
    return f"""
        <div style="{box}">
            <p style="margin: 0; font-weight: 700; font-size: 18px;">{escape(c['ecoach_title'])}</p>
            <p style="margin: 8px 0 16px; color: #f3f1ec;">{escape(c['ecoach_text'])}</p>
            <a href="{ECOACH_APP_URL}" style="{button}">{escape(c['ecoach_button'])}</a>
            <p style="margin: 12px 0 0; font-size: 13px; color: #f3f1ec;">{escape(c['ecoach_computer'])} <a href="{ECOACH_WEB_URL}" style="color: #ffffff; font-weight: 700;">{escape(c['ecoach_computer_link'])}</a></p>
        </div>
    """


def _someone_lines(lang):
    c = _copy(lang)
    if lang not in ECOACH_LANGUAGES:
        return [f"{c['help_title']} {c['help_text']}", get_site_url(site_path(lang, '/help'))]
    return [c['ecoach_text_line'], ECOACH_APP_URL, f"{c['ecoach_computer_line']} {ECOACH_WEB_URL}"]


def build_action_plan_email(first_name, summary, sections, lang='en', country=None):
    c = _copy(lang)
    greeting = _greeting(first_name, lang)
    plan_url = get_site_url(site_path(lang, '/action-plan'))
    ordered = _ordered_sections(sections, lang)
    has_safety = bool(ordered) and ordered[0]['heading'] == c['safety_heading']

    summary_html = ''.join(f'<li style="margin-bottom: 4px;">{escape(line)}</li>' for line in summary)
    sections_html = ''
    for index, section in enumerate(ordered):
        sections_html += _section_html(section)
        # Someone to talk to goes right after the safety plan, or after the summary.
        if index == 0 and has_safety:
            sections_html += _someone_html(lang)
    if not has_safety:
        sections_html = _someone_html(lang) + sections_html

    html = page_html(f"""
                <p style="margin: 0;">{escape(greeting)}</p>
                <h1 style="font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 34px; line-height: 1.1; margin: 16px 0 0;">{escape(c['plan_title'])}</h1>
                <p style="margin: 12px 0 0;">{escape(c['plan_intro'])}</p>

                <div style="margin-top: 24px; background-color: {SAGE_LIGHT}; border-radius: 14px; padding: 18px 20px;">
                    <p style="margin: 0; font-weight: 700;">{escape(c['answers_showed'])}</p>
                    <ul style="margin: 8px 0 0; padding-left: 20px;">{summary_html}</ul>
                    <p style="margin: 8px 0 0; font-size: 13px;">{escape(c['not_diagnosis'])}</p>
                </div>

                {sections_html}

                {crisis_html(lang, country)}

                {button_html(plan_url, c['open_plan'], c['or_open_link'])}

                <p style="margin: 24px 0 0; font-size: 12px; color: {TEAL};">{escape(c['plan_footer'])}</p>
    """, lang)

    lines = [greeting, '', c['plan_title'], '', c['answers_showed'] + colon(lang).rstrip()]
    lines += [f'- {line}' for line in summary]
    lines.append(c['not_diagnosis'])
    for index, section in enumerate(ordered):
        if index == 0 and not has_safety:
            lines += [''] + _someone_lines(lang)
        lines += ['', section['heading']]
        if section.get('intro'):
            lines.append(section['intro'])
        for item in section['items']:
            lines += ['', item['title']]
            if item['detail']:
                lines.append(item['detail'])
            for number, step in enumerate(item.get('steps') or [], start=1):
                lines.append(f'  {number}. {step}')
            if item.get('link'):
                lines.append(_absolute(item['link']))
        if index == 0 and has_safety:
            lines += [''] + _someone_lines(lang)
    lines += ['', crisis_text(lang, country), '', f"{c['open_plan']}{colon(lang)}{plan_url}"]

    return '\n'.join(lines), html


def send_action_plan_email(email, first_name, summary, sections, lang='en', country=None):
    text, html = build_action_plan_email(first_name, summary, sections, lang, country)
    message = EmailMultiAlternatives(
        _copy(lang)['plan_subject'],
        text,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    message.attach_alternative(html, 'text/html')
    return message.send(fail_silently=False)


def build_check_in_email(first_name, lang='en', country=None):
    c = _copy(lang)
    greeting = _greeting(first_name, lang)
    plan_url = get_site_url(site_path(lang, '/action-plan'))

    html = page_html(f"""
                <p style="margin: 0;">{escape(greeting)}</p>
                <h1 style="font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 34px; line-height: 1.1; margin: 16px 0 0;">{escape(c['check_in_title'])}</h1>
                <p style="margin: 12px 0 0;">{escape(c['check_in_intro'])}</p>
                <p style="margin: 12px 0 0;">{escape(c['check_in_ask'])}</p>
                <p style="margin: 20px 0 0;"><a href="{plan_url}" style="display: inline-block; background-color: {BROWN}; color: #ffffff; padding: 14px 24px; border-radius: 12px; text-decoration: none; font-weight: 700;">{escape(c['check_in_button'])}</a></p>

                <div style="margin-top: 28px; background-color: {SAGE_LIGHT}; border-radius: 14px; padding: 18px 20px;">
                    <p style="margin: 0; font-weight: 700;">{escape(c['missed_title'])}</p>
                    <p style="margin: 6px 0 0;">{escape(c['missed_text'])}</p>
                </div>

                {_someone_html(lang)}

                {crisis_html(lang, country)}

                <p style="margin: 28px 0 0; font-size: 12px; color: {TEAL};">{escape(c['check_in_footer'])}</p>
    """, lang)

    text = '\n'.join([
        greeting,
        '',
        c['check_in_title'],
        '',
        c['check_in_intro'],
        c['check_in_ask'],
        plan_url,
        '',
        f"{c['missed_title']} {c['missed_text']}",
        '',
        *_someone_lines(lang),
        '',
        crisis_text(lang, country),
        '',
        c['check_in_footer'],
    ])
    return text, html


def send_check_in_email(email, first_name, lang='en', country=None):
    text, html = build_check_in_email(first_name, lang, country)
    message = EmailMultiAlternatives(
        _copy(lang)['check_in_subject'],
        text,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    message.attach_alternative(html, 'text/html')
    return message.send(fail_silently=False)
