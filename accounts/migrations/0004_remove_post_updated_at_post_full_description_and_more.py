# Generated by Django 4.2.4 on 2023-08-07 11:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_comment_is_published"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="updated_at",
        ),
        migrations.AddField(
            model_name="post",
            name="full_description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="post",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="post_images/"),
        ),
        migrations.AddField(
            model_name="post",
            name="short_description",
            field=models.TextField(default=django.utils.timezone.now, max_length=200),
        ),
        migrations.AlterField(
            model_name="post",
            name="is_draft",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="post",
            name="title",
            field=models.CharField(max_length=200),
        ),
    ]
