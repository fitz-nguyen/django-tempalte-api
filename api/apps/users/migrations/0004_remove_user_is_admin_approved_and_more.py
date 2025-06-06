# Generated by Django 5.1.1 on 2024-11-08 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_remove_campaigninvite_actor_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_admin_approved",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_demo_account",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_demo_account_ready",
        ),
        migrations.RemoveField(
            model_name="user",
            name="service_category",
        ),
        migrations.AddField(
            model_name="user",
            name="created_via",
            field=models.CharField(choices=[("admin", "admin"), ("web", "web")], default="web", max_length=10),
        ),
        migrations.AddField(
            model_name="user",
            name="is_approved",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether this user should be treated as approved.",
                verbose_name="approved",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="is_sent_mail_approve_account",
            field=models.BooleanField(default=False),
        ),
    ]
