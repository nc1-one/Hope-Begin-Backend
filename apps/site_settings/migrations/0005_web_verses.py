from django.db import migrations

# The Hopeful Beginning page quoted two verses in NIV wording, which isn't
# in the public domain. The site quotes the World English Bible elsewhere
# (src/lib/blog/verses.ts in the frontend); these are the same words.
CHANGES = [
    (
        "He heals the brokenhearted and binds up their wounds.",
        "He heals the broken in heart, and binds up their wounds.",
    ),
    (
        "We have this hope as an anchor for the soul, firm and secure.",
        "This hope we have as an anchor of the soul, a hope both sure and "
        "steadfast and entering into that which is within the veil;",
    ),
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
        for field in JSON_FIELDS:
            setattr(content, field, swap(getattr(content, field), mapping))
        content.save()


def forwards(apps, schema_editor):
    apply(apps, dict(CHANGES))


def backwards(apps, schema_editor):
    apply(apps, {new: old for old, new in CHANGES})


class Migration(migrations.Migration):
    """World English Bible verses on the Hopeful Beginning page. Text edited
    in the admin is left alone."""

    dependencies = [
        ('site_settings', '0004_plainer_journey_copy'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
