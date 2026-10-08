from html import escape

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from common.utils import append_visit_site_text, get_site_url, visit_site_html

# May Himala Every Day's Facebook page. m.me opens the Messenger app on a
# phone; on a computer it stops at a messenger.com login, so the email also
# links to the page's chat on facebook.com.
ECOACH_PAGE_ID = '352008124672499'
ECOACH_APP_URL = f'https://m.me/{ECOACH_PAGE_ID}'
ECOACH_WEB_URL = f'https://www.facebook.com/messages/t/{ECOACH_PAGE_ID}'
SAFETY_HEADING = 'Your safety plan'

BROWN = '#6E5F47'
SAGE = '#AEC488'
SAGE_LIGHT = '#EFF3E7'
TEAL = '#91AFAA'


def _ordered_sections(sections):
    """The safety plan always comes first."""
    safety = [s for s in sections if s['heading'] == SAFETY_HEADING]
    rest = [s for s in sections if s['heading'] != SAFETY_HEADING]
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
            f'style="color: {BROWN}; font-weight: 700;">{escape(item.get("link_label") or "Open link")}</a></p>'
        )
    detail = f'<p style="margin: 6px 0 0;">{escape(item["detail"])}</p>' if item['detail'] else ''
    return f"""
        <div style="border: 1px solid #ece9dd; border-radius: 14px; padding: 18px 20px; margin-top: 12px;">
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


def _ecoach_html():
    return f"""
        <div style="margin-top: 32px; background-color: {BROWN}; color: #ffffff; border-radius: 16px; padding: 24px;">
            <p style="margin: 0; font-weight: 700; font-size: 18px;">Want someone to journey with you?</p>
            <p style="margin: 8px 0 16px; color: #f3f1ec;">E-coaches from Himala Everyday can help you choose where to start.</p>
            <a href="{ECOACH_APP_URL}" style="display: inline-block; background-color: #ffffff; color: {BROWN}; padding: 12px 20px; border-radius: 12px; text-decoration: none; font-weight: 700;">Talk to an e-coach on Messenger</a>
            <p style="margin: 12px 0 0; font-size: 13px; color: #f3f1ec;">On a computer? <a href="{ECOACH_WEB_URL}" style="color: #ffffff; font-weight: 700;">Open the chat on Facebook</a></p>
        </div>
    """


def build_action_plan_email(first_name, summary, sections):
    greeting = f'Hi {first_name},' if first_name else 'Hi,'
    ordered = _ordered_sections(sections)
    has_safety = bool(ordered) and ordered[0]['heading'] == SAFETY_HEADING

    summary_html = ''.join(f'<li style="margin-bottom: 4px;">{escape(line)}</li>' for line in summary)
    sections_html = ''
    for index, section in enumerate(ordered):
        sections_html += _section_html(section)
        # E-coach goes right after the safety plan, or after the summary.
        if index == 0 and has_safety:
            sections_html += _ecoach_html()
    if not has_safety:
        sections_html = _ecoach_html() + sections_html

    html = f"""
    <html>
        <body style="margin: 0; padding: 24px; background-color: #fcfdfa; font-family: Arial, Helvetica, sans-serif; color: {BROWN}; line-height: 1.6;">
            <div style="max-width: 640px; margin: 0 auto; background-color: #ffffff; border-radius: 18px; padding: 32px; border: 1px solid #ece9dd;">
                <p style="margin: 0;">{escape(greeting)}</p>
                <h1 style="font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 34px; line-height: 1.1; margin: 16px 0 0;">Your Hopeful Beginning Plan</h1>
                <p style="margin: 12px 0 0;">Here is the plan you made on HopeBegins. Pick 1 or 2 daily tools and do them every day this week.</p>

                <div style="margin-top: 24px; background-color: {SAGE_LIGHT}; border-radius: 14px; padding: 18px 20px;">
                    <p style="margin: 0; font-weight: 700;">What your answers showed</p>
                    <ul style="margin: 8px 0 0; padding-left: 20px;">{summary_html}</ul>
                    <p style="margin: 8px 0 0; font-size: 13px;">This is not a diagnosis. It is a starting point.</p>
                </div>

                {sections_html}

                <div style="margin-top: 36px; border-left: 4px solid {SAGE}; padding: 4px 0 4px 16px;">
                    <p style="margin: 0; font-weight: 700;">In crisis or thinking of ending your life?</p>
                    <p style="margin: 4px 0 0;">Call the NCMH Crisis Hotline, open 24/7: <a href="tel:1553" style="color: {BROWN}; font-weight: 700;">1553</a> or <a href="tel:+639178998727" style="color: {BROWN}; font-weight: 700;">0917 899 8727</a>. If you are in immediate danger, call 911.</p>
                </div>

                {visit_site_html('/action-plan', 'Open your plan on HopeBegins')}

                <p style="margin: 24px 0 0; font-size: 12px; color: {TEAL};">You asked for this plan on hopebegins.today. We did not add you to any mailing list.</p>
            </div>
        </body>
    </html>
    """

    lines = [greeting, '', 'Your Hopeful Beginning Plan', '', 'What your answers showed:']
    lines += [f'- {line}' for line in summary]
    lines.append('This is not a diagnosis. It is a starting point.')
    for index, section in enumerate(ordered):
        if index == 0 and not has_safety:
            lines += ['', 'Want someone to journey with you? Talk to an e-coach on Messenger:', ECOACH_APP_URL, f'On a computer: {ECOACH_WEB_URL}']
        lines += ['', section['heading'].upper()]
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
            lines += ['', 'Want someone to journey with you? Talk to an e-coach on Messenger:', ECOACH_APP_URL, f'On a computer: {ECOACH_WEB_URL}']
    lines += [
        '',
        'In crisis or thinking of ending your life? Call the NCMH Crisis Hotline, open 24/7: 1553 or 0917 899 8727. If you are in immediate danger, call 911.',
    ]
    text = append_visit_site_text('\n'.join(lines), '/action-plan')

    return text, html


def send_action_plan_email(email, first_name, summary, sections):
    text, html = build_action_plan_email(first_name, summary, sections)
    message = EmailMultiAlternatives(
        'Your Hopeful Beginning Plan',
        text,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    message.attach_alternative(html, 'text/html')
    return message.send(fail_silently=False)
