# Generated by Django 5.2 on 2025-05-19 13:28

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hire", "0001_initial"),
        ("inventory", "0005_remove_motorcycle_monthly_hire_rate_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TempHireBooking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("session_uuid", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("pickup_date", models.DateField(blank=True, null=True)),
                ("pickup_time", models.TimeField(blank=True, null=True)),
                ("return_date", models.DateField(blank=True, null=True)),
                ("return_time", models.TimeField(blank=True, null=True)),
                ("has_motorcycle_license", models.BooleanField(default=False)),
                (
                    "booked_package_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("is_international_booking", models.BooleanField(default=False)),
                (
                    "booked_daily_rate",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=8, null=True
                    ),
                ),
                (
                    "total_hire_price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Calculated total price for the motorcycle hire duration only.",
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    "total_addons_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        help_text="Calculated total price for selected add-ons.",
                        max_digits=10,
                    ),
                ),
                (
                    "total_package_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        help_text="Calculated total price for the selected package.",
                        max_digits=10,
                    ),
                ),
                (
                    "grand_total",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Sum of total_hire_price, total_addons_price, and total_package_price.",
                        max_digits=10,
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "driver_profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="temp_hire_bookings",
                        to="hire.driverprofile",
                    ),
                ),
                (
                    "motorcycle",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="temp_hire_bookings",
                        to="inventory.motorcycle",
                    ),
                ),
                (
                    "package",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="temp_hire_bookings",
                        to="hire.package",
                    ),
                ),
            ],
            options={
                "verbose_name": "Temporary Hire Booking",
                "verbose_name_plural": "Temporary Hire Bookings",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TempBookingAddOn",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "booked_addon_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=8, null=True
                    ),
                ),
                (
                    "addon",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="temp_addon_bookings",
                        to="hire.addon",
                    ),
                ),
                (
                    "temp_booking",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="temp_booking_addons",
                        to="hire.temphirebooking",
                    ),
                ),
            ],
            options={
                "verbose_name": "Temporary Booking Add-On",
                "verbose_name_plural": "Temporary Booking Add-Ons",
                "unique_together": {("temp_booking", "addon")},
            },
        ),
    ]
