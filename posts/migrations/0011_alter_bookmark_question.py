# Generated by Django 3.2 on 2022-06-20 01:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_questionpagehit_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmark',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to='posts.question'),
        ),
    ]
