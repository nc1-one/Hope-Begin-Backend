from django.db import migrations


def switch_off_old_templates(apps, schema_editor):
    """
    The dashboard templates still on were edited from the old English days,
    which quoted the NIV. Every English subscriber now gets the reviewed
    built-in days; each template stays in the dashboard, where saving it
    switches it back on for its day.
    """
    EmailTemplate = apps.get_model('daily_hope', 'EmailTemplate')
    EmailTemplate.objects.filter(is_active=True).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('daily_hope', '0006_retire_unedited_templates'),
    ]

    operations = [
        migrations.RunPython(switch_off_old_templates, migrations.RunPython.noop),
    ]
