# Generated by Django 3.1 on 2020-10-18 22:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_auto_20201018_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='expenses', to='finance.category'),
        ),
        migrations.AlterField(
            model_name='income',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='incomes', to='finance.category'),
        ),
        migrations.AlterField(
            model_name='recurringincome',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recincomes', to='finance.category'),
        ),
        migrations.AlterField(
            model_name='recurringpayment',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recpayments', to='finance.category'),
        ),
    ]