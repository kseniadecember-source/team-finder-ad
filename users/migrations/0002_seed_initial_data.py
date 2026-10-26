import sys

from django.db import migrations


def forwards_func(apps, schema_editor):
    if "test" in sys.argv:
        return
    from users.management.commands.seed_data import seed_initial_data

    seed_initial_data()


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
        ("projects", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
