from django.db import migrations, models

# (old, new) pairs for the Hopeful Beginning journey copy.
CHANGES = [
    (
        "A journey toward hope, one step at a time.",
        "Five short steps for when you feel hopeless.",
    ),
    (
        "It's okay to feel this way. You're not broken - you're here, and that matters.\n"
        "We've prepared a short journey for you. Take it at your own pace.",
        "Feeling hopeless is hard. Thank you for coming here.\n"
        "There are five short steps. Move to the next one whenever you're ready.",
    ),
    ("A guided prayer to help you exhale", "A guided prayer"),
    (
        "A devotional about the true meaning of hope",
        "A short reading on what the Bible says about hope",
    ),
    ("Gentle next steps when you're ready", "Ways to get more support"),
    (
        "Let's take a moment together. Follow each step at your own pace.",
        "Read each step slowly. Pray the words, or just read them.",
    ),
    (
        "Let's take a moment together. Quiet your thoughts for just a second. "
        "You are in a safe place.",
        "Sit still for a moment. Let your shoulders drop and breathe slowly.",
    ),
    (
        "Acknowledge the heavy feelings without judgment. It's okay to not be "
        "okay right now. Breath in slowly...",
        "Name what you're feeling, like sadness, fear or tiredness, without "
        "judging yourself for it. Breathe in slowly.",
    ),
    (
        "I release my fear, my pain, and my worry into Your hands. I don't "
        "have to carry this alone. You said to cast my burdens on You - so "
        "here they are.",
        "Lord, I give You my fear, my pain and my worry. You said to cast my "
        "burdens on You, so here they are.",
    ),
    (
        "I rest in You, Lord. Not because everything is okay, but because You "
        "are okay, and You are with me. Amen.",
        "I rest in You, Lord. Things are not okay right now, but You are with "
        "me. Amen.",
    ),
    ("A short devotional to anchor your heart.", "A short reading on hope."),
    (
        "Hope is not the absence of pain - it's the belief that pain is not "
        "the final word. It's that quiet voice inside saying, \"There's more "
        "ahead for you.\"",
        "In the Bible, hope is trust that God will keep His promises, even "
        "when you can't yet see how.",
    ),
    (
        "The Bible describes hope as an anchor for the soul - firm and secure. "
        "Not because life is easy, but because the One who holds tomorrow also "
        "holds you today. Even when you can't see it, hope is there.",
        "Hebrews calls hope an anchor for the soul. An anchor doesn't stop the "
        "storm. It keeps the boat from drifting until the storm passes.",
    ),
    (
        "You are loved - not because of what you've done, but because of who you are. "
        "God sent His Son, Jesus, so that you would never have to walk through "
        "darkness alone. He meets you right here, right now, exactly as you are.",
        "God loves you, and that love doesn't depend on what you've done. He "
        "sent His Son, Jesus, so you would never walk through darkness alone. "
        "You can come to Him as you are today.",
    ),
    (
        "What would it look like to believe - even just a little - that tomorrow "
        "could be different?",
        "What would change if you believed, even a little, that tomorrow could "
        "be different?",
    ),
    (
        "You've made it through this journey, and that matters more than you know. "
        "Whenever you're ready, here are some ways to keep going.",
        "You've finished all five steps. Here are ways to keep going.",
    ),
    ("If you're in crisis, please reach out:", "In crisis? Call one of these lines:"),
]

JSON_FIELDS = [
    'steps',
    'welcome_section',
    'word_section',
    'prayer_section',
    'devotional_section',
    'next_steps_section',
    'crisis_section',
]


def swap(value, mapping):
    """Replace text that still matches an old string exactly, at any depth."""
    if isinstance(value, str):
        return mapping.get(value, value)
    if isinstance(value, list):
        return [swap(item, mapping) for item in value]
    if isinstance(value, dict):
        return {key: swap(item, mapping) for key, item in value.items()}
    return value


def apply(apps, mapping):
    JourneyContent = apps.get_model('site_settings', 'JourneyContent')
    for content in JourneyContent.objects.all():
        content.page_subtitle = swap(content.page_subtitle, mapping)
        for field in JSON_FIELDS:
            setattr(content, field, swap(getattr(content, field), mapping))
        content.save()


def forwards(apps, schema_editor):
    apply(apps, dict(CHANGES))


def backwards(apps, schema_editor):
    apply(apps, {new: old for old, new in CHANGES})


class Migration(migrations.Migration):
    """Plainer Hopeful Beginning copy. Text edited in the admin is left alone."""

    dependencies = [
        ('site_settings', '0003_journeycontent_full_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journeycontent',
            name='page_subtitle',
            field=models.TextField(default='Five short steps for when you feel hopeless.'),
        ),
        migrations.RunPython(forwards, backwards),
    ]
