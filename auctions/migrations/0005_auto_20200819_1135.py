# Generated by Django 3.0.8 on 2020-08-19 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_bid_listing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='starting_bid',
        ),
        migrations.AlterField(
            model_name='bid',
            name='amount',
            field=models.FloatField(null=True),
        ),
    ]