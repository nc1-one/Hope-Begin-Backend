# Deutsch für Deutschland, Österreich und die Schweiz, in der Du-Form.
# Die Begriffe sind dieselben wie auf der Website: Plan, Übung, Check-in,
# Hilfetelefon, Krisentelefon, Hope Carrier, Daily Hope.

# The plan email and the check-in a week later.
PLAN = {
    'greeting': 'Hallo {name},',
    'greeting_no_name': 'Hallo,',
    # Must match the safety plan heading the site sends with the plan.
    'safety_heading': 'Dein Sicherheitsplan',
    'plan_subject': 'Dein Plan von HopeBegins',
    'plan_title': 'Ein hoffnungsvoller Anfang: dein Plan',
    'plan_intro': 'Hier ist der Plan, den du bei HopeBegins gemacht hast. Such dir 1 oder 2 tägliche Übungen aus und mach sie in den nächsten 4 Wochen an den meisten Tagen.',
    'answers_showed': 'Was deine Antworten gezeigt haben',
    'not_diagnosis': 'Das ist keine Diagnose. Es hilft dir zu entscheiden, wo du anfängst.',
    'open_plan': 'Deinen Plan bei HopeBegins öffnen',
    'or_open_link': 'Oder öffne diesen Link:',
    'plan_footer': 'Du hast diesen Plan auf hopebegins.today angefordert. Wir haben dich in keinen Newsletter eingetragen.',
    # The e-coach, for English and Taglish only.
    'ecoach_title': 'Möchtest du das mit jemandem zusammen angehen?',
    'ecoach_text': 'Die E-Coaches von Himala Everyday helfen dir zu entscheiden, wo du anfängst. Sie schreiben auf Englisch und Filipino.',
    'ecoach_button': 'Einem E-Coach im Messenger schreiben',
    'ecoach_computer': 'Am Computer?',
    'ecoach_computer_link': 'Den Chat auf Facebook öffnen',
    'ecoach_text_line': 'Möchtest du das mit jemandem zusammen angehen? Schreib einem E-Coach im Messenger:',
    'ecoach_computer_line': 'Am Computer:',
    # In place of the e-coach in the other languages: the help page.
    'help_title': 'Möchtest du mit jemandem reden?',
    'help_text': 'Hier findest du die kostenlosen Hilfetelefone in deinem Land. Mit Hope AI kannst du rund um die Uhr schreiben.',
    'help_button': 'Kostenlose Hilfe in deinem Land finden',
    # The crisis line for the visitor's country. {numbers} is "0800 111 0 111 oder 0800 111 0 222".
    'crisis_title': 'Bist du in einer Krise oder denkst du daran, dir das Leben zu nehmen?',
    'crisis_call_all_day': 'Ruf jetzt an: {numbers} ({name}, rund um die Uhr erreichbar).',
    'crisis_call': 'Ruf jetzt an: {numbers} ({name}).',
    'crisis_or': 'oder',
    'crisis_danger': 'Bei akuter Gefahr ruf die {emergency} an.',
    'crisis_nowhere': 'Finde ein kostenloses Krisentelefon in deinem Land:',
    'crisis_nowhere_danger': 'Bei akuter Gefahr ruf den Notruf deines Landes an.',
    'check_in_subject': 'Wie geht es dir diese Woche?',
    'check_in_title': 'Wie geht es dir diese Woche?',
    'check_in_intro': 'Vor einer Woche hast du bei HopeBegins deinen Plan gemacht und uns gebeten, nachzufragen, wie es dir geht.',
    'check_in_ask': 'Mach den Check-in noch einmal. Er dauert 2 Minuten und zeigt dir, was sich seit letzter Woche verändert hat.',
    'check_in_button': 'Check-in machen',
    'missed_title': 'Ein paar Tage mit deiner Übung verpasst?',
    'missed_text': 'Das passiert vielen. Fang heute wieder an. Ein verpasster Tag macht deinen Fortschritt nicht zunichte.',
    'check_in_footer': 'Um diese eine E-Mail hast du gebeten, als du auf hopebegins.today deinen Plan gemacht hast. Deine E-Mail-Adresse haben wir jetzt von unserer Check-in-Liste gelöscht.',
}

# Daily Hope: one email a day for 21 days. The days themselves are in
# apps/daily_hope/journey.
DAILY = {
    'subject': 'Daily Hope, Tag {day} von 21: {title}',
    'day_label': 'Tag {day} von 21',
    'greeting': 'Hallo {name},',
    'reflect_label': 'Zum Nachdenken für heute',
    'prayer_label': 'Ein kurzes Gebet',
    'team': 'Das Team von HopeBegins',
    'more_label': 'Mehr von HopeBegins',
    'prayers_link': 'Jemanden bitten, für dich zu beten',
    'support_link': 'HopeBegins unterstützen',
    'visit': 'HopeBegins öffnen',
    'or_open_link': 'Oder öffne diesen Link:',
    'footer': 'Du bekommst diese E-Mails, weil du dich auf hopebegins.today für Daily Hope angemeldet hast. Es sind insgesamt 21.',
    'stop': 'Diese E-Mails abbestellen',
    'stop_confirm': 'Möchtest du keine E-Mails von Daily Hope mehr bekommen?',
    # Plain-text version of an email written in the admin dashboard.
    'template_text': 'Tag {day} von Daily Hope ist da. Um alles zu lesen, öffne diese E-Mail in einer App, die Formatierungen anzeigt.',
    # The answer to signing up, and the page after "Stop these emails".
    'welcome': 'Du bist für Daily Hope angemeldet. Tag 1 ist schon unterwegs in dein Postfach.',
    'stopped_title': 'Du bekommst keine E-Mails von Daily Hope mehr.',
    'stopped_text': 'Wenn du es dir anders überlegst, kannst du dich bei HopeBegins wieder anmelden.',
    'stopped_back': 'Zu HopeBegins',
}

# The email sent when a Hope Carrier has prayed for someone.
PRAYER = {
    'subject': 'Ein Hope Carrier hat heute für dich gebetet',
    'greeting': 'Hallo {name},',
    'greeting_no_name': 'Hallo,',
    'prayed': 'Ein Hope Carrier hat heute für dein Anliegen gebetet.',
    'note': 'Dazu gibt es ein paar Zeilen für dich:',
    'praying_with_you': 'Wir beten mit dir.',
    # English and Taglish: the e-coach. Other languages: the help page.
    'ecoach': 'Wenn du mit jemandem reden möchtest, schreib einem E-Coach im Messenger:',
    'ecoach_computer': 'Am Computer:',
    'help': 'Wenn du mit jemandem reden möchtest, findest du hier die kostenlosen Hilfetelefone in deinem Land:',
    'sign_off': 'HopeBegins',
}
