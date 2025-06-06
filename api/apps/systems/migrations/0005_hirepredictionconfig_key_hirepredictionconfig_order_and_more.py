# Generated by Django 5.1.1 on 2025-03-11 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("systems", "0004_hirepredictionconfig_homesizeconfig_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirepredictionconfig",
            name="key",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="hirepredictionconfig",
            name="order",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="homesizeconfig",
            name="description",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="homesizeconfig",
            name="order",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="roofmaterialconfig",
            name="key",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="roofmaterialconfig",
            name="order",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="salestatusconfig",
            name="hex_color",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="salestatusconfig",
            name="key",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="salestatusconfig",
            name="order",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="stormdamageconfig",
            name="order",
            field=models.IntegerField(default=0),
        ),
    ]
