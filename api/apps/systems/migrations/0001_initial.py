# Generated by Django 2.2.7 on 2024-09-23 10:25

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import tinymce.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContentTalkConfig',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('Contact Visit', 'Contact Visit'), ('Contact Mail', 'Contact Mail'), ('Contact Digital', 'Contact Digital'), ('Contact Call Text', 'Contact Call Text')], default='Contact Visit', max_length=30)),
                ('title', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Content Talk',
                'verbose_name_plural': 'Content Talk Config',
            },
        ),
        migrations.CreateModel(
            name='PageConfig',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('content', tinymce.models.HTMLField(blank=True, null=True)),
                ('type', models.CharField(choices=[('Learn more - Web', 'Learn more - Web'), ('Terms of Service - Mobile', 'Terms of Service - Mobile'), ('Terms of Service - Web', 'Terms of Service - Web'), ('Privacy Policy - Web', 'Privacy Policy - Web'), ('Privacy Policy - Mobile', 'Privacy Policy - Mobile')], default='Learn more - Web', max_length=100)),
                ('published', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Page Content',
                'verbose_name_plural': 'Page Contents',
                'ordering': ['-created'],
            },
        ),
    ]
