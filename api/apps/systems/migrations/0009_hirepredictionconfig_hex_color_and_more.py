# Generated by Django 5.1.1 on 2025-03-14 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("systems", "0008_alter_stormdamageconfig_unit_value_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirepredictionconfig",
            name="hex_color",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="hirepredictionconfig",
            name="icon_url",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
