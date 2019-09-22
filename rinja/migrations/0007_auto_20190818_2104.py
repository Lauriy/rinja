# Generated by Django 2.2.4 on 2019-08-18 21:04

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rinja', '0006_auto_20190818_2032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='latest_real_market_cap',
            field=djmoney.models.fields.MoneyField(blank=True, currency_choices=[('EUR', 'Euro')], decimal_places=2, default_currency='EUR', max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='nominal_market_cap',
            field=djmoney.models.fields.MoneyField(blank=True, currency_choices=[('EUR', 'Euro')], decimal_places=2, default_currency='EUR', max_digits=20, null=True),
        ),
    ]