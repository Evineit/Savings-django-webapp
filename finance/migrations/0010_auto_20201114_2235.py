# Generated by Django 3.1 on 2020-11-14 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0009_auto_20201109_0230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurringpayment',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]