# Generated by Django 4.2.6 on 2023-10-21 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0005_alter_report_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(choices=[('Running', 'Running'), ('Complete', 'Complete'), ('Failed', 'Failed')], default='Running', max_length=8),
        ),
    ]
