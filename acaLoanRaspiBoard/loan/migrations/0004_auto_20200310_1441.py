# Generated by Django 3.0.3 on 2020-03-10 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0003_auto_20200310_1331'),
    ]

    operations = [
        migrations.RenameField(
            model_name='semester',
            old_name='current_semester',
            new_name='semester',
        ),
    ]