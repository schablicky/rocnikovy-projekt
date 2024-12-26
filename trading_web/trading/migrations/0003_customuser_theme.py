# Generated by Django 5.1.3 on 2024-12-26 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0002_alter_customuser_apikey'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='theme',
            field=models.CharField(choices=[('light', 'Light'), ('dark', 'Dark')], default='light', max_length=5),
        ),
    ]