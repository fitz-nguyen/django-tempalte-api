# Generated by Django 5.1.1 on 2025-03-12 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("systems", "0006_systemconfig_facebook_page_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="homesizeconfig",
            name="value",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="stormdamageconfig",
            name="unit_value",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
