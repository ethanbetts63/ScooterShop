# Generated by Django 5.2 on 2025-05-21 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "hire",
            "0007_rename_license_issuing_country_driverprofile_international_license_issuing_country_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="hirebooking",
            name="currency",
            field=models.CharField(
                default="AUD",
                help_text="The three-letter ISO currency code for the booking.",
                max_length=3,
            ),
        ),
        migrations.AddField(
            model_name="temphirebooking",
            name="currency",
            field=models.CharField(
                default="AUD",
                help_text="The three-letter ISO currency code for the booking.",
                max_length=3,
            ),
        ),
        migrations.AddField(
            model_name="temphirebooking",
            name="deposit_amount",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="The deposit amount required for the booking.",
                max_digits=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="temphirebooking",
            name="payment_option",
            field=models.CharField(
                blank=True,
                choices=[
                    ("online_full", "Online (Full Payment)"),
                    ("online_deposit", "Online (Deposit Only)"),
                    ("in_store", "Pay In Store"),
                ],
                help_text="The selected payment option for this booking.",
                max_length=20,
                null=True,
            ),
        ),
    ]
