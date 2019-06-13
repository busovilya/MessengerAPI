# Generated by Django 2.2.2 on 2019-06-13 12:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_auto_20190605_1438'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='conversation',
        ),
        migrations.AddField(
            model_name='message',
            name='chat',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.Chat'),
            preserve_default=False,
        ),
    ]
