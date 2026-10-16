from html import escape

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from common.utils import get_site_url

# May Himala Every Day's Facebook page. m.me opens the Messenger app on a
# phone; on a computer it stops at a messenger.com login, so the email also
# links to the page's chat on facebook.com.
ECOACH_PAGE_ID = '352008124672499'
ECOACH_APP_URL = f'https://m.me/{ECOACH_PAGE_ID}'
ECOACH_WEB_URL = f'https://www.facebook.com/messages/t/{ECOACH_PAGE_ID}'

BROWN = '#6E5F47'
SAGE = '#AEC488'
SAGE_LIGHT = '#EFF3E7'
TEAL = '#91AFAA'

LANGUAGES = ('en', 'tl')

# Wrapper text for both emails. The plan itself arrives already written in
# the visitor's language.
COPY = {
    'en': {
        'greeting': 'Hi {name},',
        'greeting_no_name': 'Hi,',
        'safety_heading': 'Your safety plan',
        'plan_subject': 'Your Hopeful Beginning Plan',
        'plan_title': 'Your Hopeful Beginning Plan',
        'plan_intro': 'Here is the plan you made on HopeBegins. Pick 1 or 2 daily tools and use them on most days for the next 4 weeks.',
        'answers_showed': 'What your answers showed',
        'not_diagnosis': "This isn't a diagnosis. It helps you pick where to start.",
        'open_plan': 'Open your plan on HopeBegins',
        'or_open_link': 'Or open this link:',
        'plan_footer': 'You asked for this plan on hopebegins.today. We did not add you to any mailing list.',
        'ecoach_title': 'Want someone to go through this with you?',
        'ecoach_text': 'E-coaches from Himala Everyday can help you choose where to start.',
        'ecoach_button': 'Talk to an e-coach on Messenger',
        'ecoach_computer': 'On a computer?',
        'ecoach_computer_link': 'Open the chat on Facebook',
        'ecoach_text_line': 'Want someone to go through this with you? Talk to an e-coach on Messenger:',
        'ecoach_computer_line': 'On a computer:',
        'crisis_title': 'In crisis or thinking of ending your life?',
        'crisis_call': 'Call the NCMH Crisis Hotline, open 24/7:',
        'crisis_or': 'or',
        'crisis_danger': 'If you are in immediate danger, call 911.',
        'check_in_subject': 'How are you doing this week?',
        'check_in_title': 'How are you doing this week?',
        'check_in_intro': 'A week ago you made your Hopeful Beginning Plan on HopeBegins and asked us to check on you.',
        'check_in_ask': 'Take the check-in again. It takes 2 minutes and shows what has changed since last week.',
        'check_in_button': 'Take the check-in',
        'missed_title': 'Missed some days with your tool?',
        'missed_text': "That's normal. Start again today. A missed day doesn't undo your progress.",
        'check_in_footer': 'You asked for this one email when you made your plan on hopebegins.today. We have now deleted your email address from our check-in list.',
    },
    'tl': {
        'greeting': 'Hi {name},',
        'greeting_no_name': 'Hi,',
        'safety_heading': 'Ang safety plan mo',
        'plan_subject': 'Ang Hopeful Beginning Plan mo',
        'plan_title': 'Ang Hopeful Beginning Plan mo',
        'plan_intro': 'Ito ang planong ginawa mo sa HopeBegins. Pumili ng 1 o 2 daily tool at gamitin ang mga ito sa karamihan ng araw sa susunod na 4 na linggo.',
        'answers_showed': 'Ang ipinakita ng mga sagot mo',
        'not_diagnosis': 'Hindi ito diagnosis. Tinutulungan ka lang nitong pumili kung saan magsisimula.',
        'open_plan': 'Buksan ang plano mo sa HopeBegins',
        'or_open_link': 'O buksan ang link na ito:',
        'plan_footer': 'Hiningi mo ang planong ito sa hopebegins.today. Hindi ka namin isinama sa anumang mailing list.',
        'ecoach_title': 'Gusto mo ba ng kasama sa pinagdadaanan mo?',
        'ecoach_text': 'Matutulungan ka ng mga e-coach ng Himala Everyday na pumili kung saan magsisimula.',
        'ecoach_button': 'Kausapin ang e-coach sa Messenger',
        'ecoach_computer': 'Nasa computer ka?',
        'ecoach_computer_link': 'Buksan ang chat sa Facebook',
        'ecoach_text_line': 'Gusto mo ba ng kasama sa pinagdadaanan mo? Kausapin ang e-coach sa Messenger:',
        'ecoach_computer_line': 'Sa computer:',
        'crisis_title': 'Nasa crisis ka ba o naiisip mong tapusin ang buhay mo?',
        'crisis_call': 'Tumawag sa NCMH Crisis Hotline, bukas 24/7:',
        'crisis_or': 'o',
        'crisis_danger': 'Kung nasa panganib ka ngayon, tumawag sa 911.',
        'check_in_subject': 'Kumusta ka ngayong linggo?',
        'check_in_title': 'Kumusta ka ngayong linggo?',
        'check_in_intro': 'Isang linggo na mula nang gawin mo ang Hopeful Beginning Plan mo sa HopeBegins at sinabi mong kumustahin ka namin.',
        'check_in_ask': 'Sagutan ulit ang check-in. 2 minuto lang ito at ipapakita nito kung ano ang nagbago mula noong nakaraang linggo.',
        'check_in_button': 'Sagutan ang check-in',
        'missed_title': 'May mga araw bang hindi mo nagawa ang tool mo?',
        'missed_text': 'Normal lang iyan. Ituloy lang ngayong araw. Hindi nabubura ang progress mo dahil sa isang araw na hindi nagawa.',
        'check_in_footer': 'Ikaw ang humiling ng email na ito noong ginawa mo ang plano mo sa hopebegins.today. Inalis na namin ang email mo sa listahan ng check-in.',
    },
}


def _copy(lang):
    return COPY.get(lang, COPY['en'])


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


def _ecoach_html(lang='en'):
    c = _copy(lang)
    return f"""
        <div style="margin-top: 32px; background-color: {BROWN}; color: #ffffff; border-radius: 16px; padding: 24px;">
            <p style="margin: 0; font-weight: 700; font-size: 18px;">{c['ecoach_title']}</p>
            <p style="margin: 8px 0 16px; color: #f3f1ec;">{c['ecoach_text']}</p>
            <a href="{ECOACH_APP_URL}" style="display: inline-block; background-color: #ffffff; color: {BROWN}; padding: 12px 20px; border-radius: 12px; text-decoration: none; font-weight: 700;">{c['ecoach_button']}</a>
            <p style="margin: 12px 0 0; font-size: 13px; color: #f3f1ec;">{c['ecoach_computer']} <a href="{ECOACH_WEB_URL}" style="color: #ffffff; font-weight: 700;">{c['ecoach_computer_link']}</a></p>
        </div>
    """


def _ecoach_lines(lang):
    c = _copy(lang)
    return [c['ecoach_text_line'], ECOACH_APP_URL, f"{c['ecoach_computer_line']} {ECOACH_WEB_URL}"]


def crisis_text(lang='en'):
    c = _copy(lang)
    return f"{c['crisis_title']} {c['crisis_call']} 1553 {c['crisis_or']} 0917 899 8727. {c['crisis_danger']}"


def _crisis_html(lang='en'):
    c = _copy(lang)
    return f"""
        <div style="margin-top: 36px; border-left: 4px solid {SAGE}; padding: 4px 0 4px 16px;">
            <p style="margin: 0; font-weight: 700;">{c['crisis_title']}</p>
            <p style="margin: 4px 0 0;">{c['crisis_call']} <a href="tel:1553" style="color: {BROWN}; font-weight: 700;">1553</a> {c['crisis_or']} <a href="tel:+639178998727" style="color: {BROWN}; font-weight: 700;">0917 899 8727</a>. {c['crisis_danger']}</p>
        </div>
    """


def _button_html(url, label, lang):
    c = _copy(lang)
    return f"""
        <div style="margin: 32px 0; text-align: center;">
            <a href="{url}" style="display: inline-block; background-color: {BROWN}; color: #ffffff; padding: 14px 24px; border-radius: 12px; text-decoration: none; font-weight: 700;">{escape(label)}</a>
            <p style="margin: 12px 0 0; font-size: 13px;">{c['or_open_link']} <a href="{url}" style="color: {BROWN};">{url}</a></p>
        </div>
    """


def _page(body):
    return f"""
    <html>
        <body style="margin: 0; padding: 24px; background-color: #fcfdfa; font-family: Arial, Helvetica, sans-serif; color: {BROWN}; line-height: 1.6;">
            <div style="max-width: 640px; margin: 0 auto; background-color: #ffffff; border-radius: 18px; padding: 32px; border: 1px solid #ece9dd;">
                {body}
            </div>
        </body>
    </html>
    """


def build_action_plan_email(first_name, summary, sections, lang='en'):
    c = _copy(lang)
    greeting = _greeting(first_name, lang)
    plan_url = get_site_url('/action-plan')
    ordered = _ordered_sections(sections, lang)
    has_safety = bool(ordered) and ordered[0]['heading'] == c['safety_heading']

    summary_html = ''.join(f'<li style="margin-bottom: 4px;">{escape(line)}</li>' for line in summary)
    sections_html = ''
    for index, section in enumerate(ordered):
        sections_html += _section_html(section)
        # E-coach goes right after the safety plan, or after the summary.
        if index == 0 and has_safety:
            sections_html += _ecoach_html(lang)
    if not has_safety:
        sections_html = _ecoach_html(lang) + sections_html

    html = _page(f"""
                <p style="margin: 0;">{escape(greeting)}</p>
                <h1 style="font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 34px; line-height: 1.1; margin: 16px 0 0;">{c['plan_title']}</h1>
                <p style="margin: 12px 0 0;">{c['plan_intro']}</p>

                <div style="margin-top: 24px; background-color: {SAGE_LIGHT}; border-radius: 14px; padding: 18px 20px;">
                    <p style="margin: 0; font-weight: 700;">{c['answers_showed']}</p>
                    <ul style="margin: 8px 0 0; padding-left: 20px;">{summary_html}</ul>
                    <p style="margin: 8px 0 0; font-size: 13px;">{c['not_diagnosis']}</p>
                </div>

                {sections_html}

                {_crisis_html(lang)}

                {_button_html(plan_url, c['open_plan'], lang)}

                <p style="margin: 24px 0 0; font-size: 12px; color: {TEAL};">{c['plan_footer']}</p>
    """)

    lines = [greeting, '', c['plan_title'], '', f"{c['answers_showed']}:"]
    lines += [f'- {line}' for line in summary]
    lines.append(c['not_diagnosis'])
    for index, section in enumerate(ordered):
        if index == 0 and not has_safety:
            lines += [''] + _ecoach_lines(lang)
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
            lines += [''] + _ecoach_lines(lang)
    lines += ['', crisis_text(lang), '', f"{c['open_plan']}: {plan_url}"]

    return '\n'.join(lines), html


def send_action_plan_email(email, first_name, summary, sections, lang='en'):
    text, html = build_action_plan_email(first_name, summary, sections, lang)
    message = EmailMultiAlternatives(
        _copy(lang)['plan_subject'],
        text,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    message.attach_alternative(html, 'text/html')
    return message.send(fail_silently=False)


def build_check_in_email(first_name, lang='en'):
    c = _copy(lang)
    greeting = _greeting(first_name, lang)
    plan_url = get_site_url('/action-plan')

    html = _page(f"""
                <p style="margin: 0;">{escape(greeting)}</p>
                <h1 style="font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 34px; line-height: 1.1; margin: 16px 0 0;">{c['check_in_title']}</h1>
                <p style="margin: 12px 0 0;">{c['check_in_intro']}</p>
                <p style="margin: 12px 0 0;">{c['check_in_ask']}</p>
                <p style="margin: 20px 0 0;"><a href="{plan_url}" style="display: inline-block; background-color: {BROWN}; color: #ffffff; padding: 14px 24px; border-radius: 12px; text-decoration: none; font-weight: 700;">{c['check_in_button']}</a></p>

                <div style="margin-top: 28px; background-color: {SAGE_LIGHT}; border-radius: 14px; padding: 18px 20px;">
                    <p style="margin: 0; font-weight: 700;">{c['missed_title']}</p>
                    <p style="margin: 6px 0 0;">{c['missed_text']}</p>
                </div>

                {_ecoach_html(lang)}

                {_crisis_html(lang)}

                <p style="margin: 28px 0 0; font-size: 12px; color: {TEAL};">{c['check_in_footer']}</p>
    """)

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
        *_ecoach_lines(lang),
        '',
        crisis_text(lang),
        '',
        c['check_in_footer'],
    ])
    return text, html


def send_check_in_email(email, first_name, lang='en'):
    text, html = build_check_in_email(first_name, lang)
    message = EmailMultiAlternatives(
        _copy(lang)['check_in_subject'],
        text,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    message.attach_alternative(html, 'text/html')
    return message.send(fail_silently=False)
