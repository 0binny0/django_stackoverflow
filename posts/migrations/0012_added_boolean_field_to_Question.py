# Generated by Django 3.2 on 2022-08-01 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_alter_bookmark_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]
