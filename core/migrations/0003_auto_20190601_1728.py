# Generated by Django 2.2.1 on 2019-06-01 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190531_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='service',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('queued', 'QUEUED'), ('started', 'STARTED'), ('done', 'DONE'), ('failed', 'FAILED')], default='queued', max_length=7),
        ),
    ]
