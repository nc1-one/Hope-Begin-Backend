# The plan email and the check-in a week later, in Latin American Spanish (tú).
PLAN = {
    'greeting': 'Hola, {name}:',
    'greeting_no_name': 'Hola:',
    # Must match the safety plan heading the site sends with the plan.
    'safety_heading': 'Tu plan de seguridad',
    'plan_subject': 'Tu plan de HopeBegins',
    'plan_title': 'Un comienzo con esperanza: tu plan',
    'plan_intro': 'Este es el plan que hiciste en HopeBegins. Elige 1 o 2 herramientas diarias y úsalas la mayoría de los días durante las próximas 4 semanas.',
    'answers_showed': 'Lo que mostraron tus respuestas',
    'not_diagnosis': 'No es un diagnóstico. Es un punto de partida.',
    'open_plan': 'Abrir tu plan en HopeBegins',
    'or_open_link': 'O abre este enlace:',
    'plan_footer': 'Pediste este plan en hopebegins.today. No te agregamos a ninguna lista de correo.',
    # The e-coach, for English and Taglish only.
    'ecoach_title': '¿Quieres que alguien te acompañe en esto?',
    'ecoach_text': 'Los e-coaches de Himala Everyday pueden ayudarte a elegir por dónde empezar.',
    'ecoach_button': 'Hablar con un e-coach en Messenger',
    'ecoach_computer': '¿Estás en una computadora?',
    'ecoach_computer_link': 'Abrir el chat en Facebook',
    'ecoach_text_line': '¿Quieres que alguien te acompañe en esto? Habla con un e-coach en Messenger:',
    'ecoach_computer_line': 'En una computadora:',
    # In place of the e-coach in the other languages: the help page.
    'help_title': '¿Quieres hablar con alguien?',
    'help_text': 'Mira las líneas gratuitas de tu país o chatea con Hope AI a cualquier hora.',
    'help_button': 'Buscar ayuda gratuita en tu país',
    # The crisis line for the visitor's country. {numbers} is "800 911 2000" or "106 o 300 754 8933".
    'crisis_title': '¿Estás en crisis o piensas en quitarte la vida?',
    'crisis_call_all_day': '{name}, abierta las 24 horas: llama al {numbers}.',
    'crisis_call': '{name}: llama al {numbers}.',
    'crisis_or': 'o',
    'crisis_danger': 'Si estás en peligro inmediato, llama al {emergency}.',
    'crisis_nowhere': 'Encuentra una línea de crisis gratuita donde estés:',
    'crisis_nowhere_danger': 'Si estás en peligro inmediato, llama al número de emergencias de tu país.',
    'check_in_subject': '¿Cómo vas esta semana?',
    'check_in_title': '¿Cómo vas esta semana?',
    'check_in_intro': 'Hace una semana hiciste tu plan en HopeBegins y nos pediste que te escribiéramos para saber cómo estás.',
    'check_in_ask': 'Vuelve a hacer el chequeo. Toma 2 minutos y te muestra qué ha cambiado desde la semana pasada.',
    'check_in_button': 'Hacer el chequeo',
    'missed_title': '¿Te saltaste algunos días con tu herramienta?',
    'missed_text': 'Es normal. Retómala hoy. Los días que te saltes no borran tu avance.',
    'check_in_footer': 'Pediste este único correo cuando hiciste tu plan en hopebegins.today. Ya borramos tu dirección de correo de nuestra lista.',
}

# Daily Hope: one email a day for 21 days. The days themselves are in
# apps/daily_hope/journey.
DAILY = {
    'subject': 'Daily Hope, día {day} de 21: {title}',
    'day_label': 'Día {day} de 21',
    'greeting': 'Hola, {name}:',
    'reflect_label': 'Para pensar hoy',
    'prayer_label': 'Una oración corta',
    'team': 'El equipo de HopeBegins',
    'more_label': 'Más de HopeBegins',
    'prayers_link': 'Pedir que oren por ti',
    'support_link': 'Apoyar a HopeBegins',
    'visit': 'Abrir HopeBegins',
    'or_open_link': 'O abre este enlace:',
    'footer': 'Recibes estos correos porque te registraste en Daily Hope en hopebegins.today. Son 21 en total.',
    'stop': 'Dejar de recibir estos correos',
    'stop_confirm': '¿Quieres dejar de recibir los correos de Daily Hope?',
    # Plain-text version of an email written in the admin dashboard.
    'template_text': 'Ya llegó el día {day} de Daily Hope. Para leerlo completo, abre este correo en una app que muestre el formato.',
    # The answer to signing up, and the page after "Stop these emails".
    'welcome': 'Te registraste en Daily Hope. El día 1 ya va en camino a tu correo.',
    'stopped_title': 'Ya no vas a recibir correos de Daily Hope.',
    'stopped_text': 'Si cambias de opinión, puedes volver a registrarte en HopeBegins.',
    'stopped_back': 'Ir a HopeBegins',
}

# When a Hope Carrier has prayed for someone's request. The request itself
# is never quoted: previews can be seen by others.
PRAYER = {
    'subject': 'Un Hope Carrier oró por ti hoy',
    'greeting': 'Hola, {name}:',
    'greeting_no_name': 'Hola:',
    'prayed': 'Hoy un Hope Carrier oró por tu petición.',
    # Hope Carriers live in the Philippines and write in English or Filipino.
    'note': 'Te escribió unas palabras (puede ser en inglés):',
    'praying_with_you': 'Estamos orando contigo.',
    # English and Taglish: the e-coach. Other languages: the help page.
    'ecoach': 'Si quieres hablar con alguien, hay un e-coach en Messenger:',
    'ecoach_computer': 'En una computadora:',
    'help': 'Si quieres hablar con alguien, aquí están las líneas gratuitas de tu país:',
    'sign_off': 'HopeBegins',
}
