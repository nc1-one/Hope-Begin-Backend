from datetime import timedelta

from django.db import migrations

# A template saved within this long of being created was never edited.
UNEDITED = timedelta(minutes=5)


def retire_unedited(apps, schema_editor):
    """
    The day templates seeded from the old content.py are switched off, so the
    rewritten days in journey/en.py go out instead. Templates someone edited
    in the dashboard stay on. Switching one back on there brings it back.
    """
    EmailTemplate = apps.get_model('daily_hope', 'EmailTemplate')
    for template in EmailTemplate.objects.filter(is_active=True):
        if template.updated_at - template.created_at < UNEDITED:
            template.is_active = False
            template.save(update_fields=['is_active'])


class Migration(migrations.Migration):

    dependencies = [
        ('daily_hope', '0005_language_and_country'),
    ]

    operations = [
        migrations.RunPython(retire_unedited, migrations.RunPython.noop),
    ]
