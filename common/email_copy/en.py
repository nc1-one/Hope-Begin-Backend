# The plan email and the check-in a week later.
PLAN = {
    'greeting': 'Hi {name},',
    'greeting_no_name': 'Hi,',
    # Must match the safety plan heading the site sends with the plan.
    'safety_heading': 'Your safety plan',
    'plan_subject': 'Your Hopeful Beginning Plan',
    'plan_title': 'Your Hopeful Beginning Plan',
    'plan_intro': 'Here is the plan you made on HopeBegins. Pick 1 or 2 daily tools and use them on most days for the next 4 weeks.',
    'answers_showed': 'What your answers showed',
    'not_diagnosis': 'This is not a diagnosis. It is a starting point.',
    'open_plan': 'Open your plan on HopeBegins',
    'or_open_link': 'Or open this link:',
    'plan_footer': 'You asked for this plan on hopebegins.today. We did not add you to any mailing list.',
    # The e-coach, for English and Taglish only.
    'ecoach_title': 'Want someone to go through this with you?',
    'ecoach_text': 'E-coaches from Himala Everyday can help you choose where to start.',
    'ecoach_button': 'Talk to an e-coach on Messenger',
    'ecoach_computer': 'On a computer?',
    'ecoach_computer_link': 'Open the chat on Facebook',
    'ecoach_text_line': 'Want someone to go through this with you? Talk to an e-coach on Messenger:',
    'ecoach_computer_line': 'On a computer:',
    # In place of the e-coach in the other languages: the help page.
    'help_title': 'Want to talk to someone?',
    'help_text': 'See the free lines in your country, or chat with Hope AI at any hour.',
    'help_button': 'Find free help where you live',
    # The crisis line for the visitor's country. {numbers} is "1553 or 0917 899 8727".
    'crisis_title': 'In crisis or thinking of ending your life?',
    'crisis_call_all_day': 'Call {name}, open 24/7: {numbers}.',
    'crisis_call': 'Call {name}: {numbers}.',
    'crisis_or': 'or',
    'crisis_danger': 'If you are in immediate danger, call {emergency}.',
    'crisis_nowhere': 'Find a free crisis line where you are:',
    'crisis_nowhere_danger': 'If you are in immediate danger, call your local emergency number.',
    'check_in_subject': 'How are you doing this week?',
    'check_in_title': 'How are you doing this week?',
    'check_in_intro': 'A week ago you made your Hopeful Beginning Plan on HopeBegins and asked us to check on you.',
    'check_in_ask': 'Take the check-in again. It takes 2 minutes and shows what has changed since last week.',
    'check_in_button': 'Take the check-in',
    'missed_title': 'Missed some days with your tool?',
    'missed_text': "That's normal. Start again today. A missed day doesn't undo your progress.",
    'check_in_footer': 'You asked for this one email when you made your plan on hopebegins.today. We have now deleted your email address from our check-in list.',
}

# Daily Hope: one email a day for 21 days. The days themselves are in
# apps/daily_hope/journey.
DAILY = {
    'subject': 'Daily Hope, day {day} of 21: {title}',
    'day_label': 'Day {day} of 21',
    'greeting': 'Hi {name},',
    'reflect_label': 'Something to think about today',
    'prayer_label': 'A short prayer',
    'team': 'The HopeBegins team',
    'more_label': 'More from HopeBegins',
    'prayers_link': 'Ask someone to pray for you',
    'support_link': 'Support HopeBegins',
    'visit': 'Open HopeBegins',
    'or_open_link': 'Or open this link:',
    'footer': 'You get these emails because you signed up for Daily Hope on hopebegins.today. There are 21 in all.',
    'stop': 'Stop these emails',
    'stop_confirm': 'Do you want to stop getting Daily Hope emails?',
    # Plain-text version of an email written in the admin dashboard.
    'template_text': 'Day {day} of Daily Hope is here. To read all of it, open this email in an app that shows formatting.',
    # The answer to signing up, and the page after "Stop these emails".
    'welcome': 'You signed up for Daily Hope. Day 1 is on its way to your inbox.',
    'stopped_title': 'You won’t get any more Daily Hope emails.',
    'stopped_text': 'If you change your mind, you can sign up again on HopeBegins.',
    'stopped_back': 'Go to HopeBegins',
}

# When a Hope Carrier has prayed for someone's request. The request itself
# is never quoted: previews can be seen by others.
PRAYER = {
    'subject': 'A Hope Carrier prayed for you today',
    'greeting': 'Hi {name},',
    'greeting_no_name': 'Hi,',
    'prayed': 'A Hope Carrier prayed for your request today.',
    'note': 'They wrote a note for you:',
    'praying_with_you': 'We are praying with you.',
    # English and Taglish: the e-coach. Other languages: the help page.
    'ecoach': 'If you want to talk to someone, an e-coach is on Messenger:',
    'ecoach_computer': 'On a computer:',
    'help': 'If you want to talk to someone, here are the free lines in your country:',
    'sign_off': 'HopeBegins',
}
