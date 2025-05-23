# payments/webhook_handlers.py
from django.db import transaction
import logging

# Import models from hire app
from hire.models import TempHireBooking, HireBooking, BookingAddOn, TempBookingAddOn
# Import Payment model from payments app
from payments.models import Payment

logger = logging.getLogger(__name__)

def handle_hire_booking_succeeded(payment_obj: Payment, payment_intent_data: dict):
    """
    Handles the business logic for a successful payment_intent.succeeded event
    specifically for a 'hire_booking'.

    This function is responsible for:
    1. Converting the TempHireBooking to a permanent HireBooking.
    2. Copying associated add-ons.
    3. Deleting the temporary booking.

    Args:
        payment_obj (Payment): The Payment model instance linked to this intent.
        payment_intent_data (dict): The data object from the Stripe PaymentIntent event.
    """
    logger.info(f"Handling successful hire_booking payment for Payment ID: {payment_obj.id}")

    try:
        # Ensure we are working within an atomic transaction for data consistency
        with transaction.atomic():
            temp_booking = payment_obj.temp_hire_booking

            # Determine payment_status for the HireBooking based on the original payment option
            hire_payment_status = 'paid' if temp_booking.payment_option == 'online_full' else 'deposit_paid'

            # Create the HireBooking instance
            hire_booking = HireBooking.objects.create(
                motorcycle=temp_booking.motorcycle,
                driver_profile=temp_booking.driver_profile,
                package=temp_booking.package,
                booked_package_price=temp_booking.booked_package_price,
                pickup_date=temp_booking.pickup_date,
                pickup_time=temp_booking.pickup_time,
                return_date=temp_booking.return_date,
                return_time=temp_booking.return_time,
                is_international_booking=temp_booking.is_international_booking,
                booked_daily_rate=temp_booking.booked_daily_rate,
                total_price=temp_booking.grand_total,
                deposit_amount=temp_booking.deposit_amount if temp_booking.deposit_amount else 0,
                amount_paid=payment_obj.amount, # Use the amount from the Payment object
                payment_status=hire_payment_status,
                payment_method='online',
                currency=temp_booking.currency,
                status='confirmed',
                payment=payment_obj, # Link the HireBooking to the Payment object
                stripe_payment_intent_id=payment_obj.stripe_payment_intent_id, # NEW: Populate this field
            )
            logger.info(f"Created new HireBooking: {hire_booking.booking_reference} from TempHireBooking {temp_booking.id}")

            # Copy add-ons from TempBookingAddOn to BookingAddOn
            temp_booking_addons = TempBookingAddOn.objects.filter(temp_booking=temp_booking)
            for temp_addon in temp_booking_addons:
                BookingAddOn.objects.create(
                    booking=hire_booking,
                    addon=temp_addon.addon,
                    quantity=temp_addon.quantity,
                    booked_addon_price=temp_addon.booked_addon_price
                )
            logger.info(f"Copied {len(temp_booking_addons)} add-ons for HireBooking {hire_booking.booking_reference}.")

            # Delete the TempHireBooking and its associated TempBookingAddOns
            temp_booking_id_to_delete = temp_booking.id
            temp_booking.delete()
            logger.info(f"TempHireBooking {temp_booking_id_to_delete} and associated data deleted.")

            # At this point, the booking is finalized. You might want to:
            # - Send a confirmation email to the user.
            # - Update inventory (if not already done).
            # - Log the final booking reference for administrative purposes.

    except TempHireBooking.DoesNotExist:
        logger.error(f"TempHireBooking not found for Payment ID {payment_obj.id}. Cannot finalize booking.")
        # Depending on your error handling, you might want to raise an exception
        # or mark the payment as needing manual review.
    except Exception as e:
        logger.exception(f"Critical error finalizing hire booking for Payment ID {payment_obj.id}: {e}")
        # Re-raise the exception to ensure the webhook returns a 500, prompting Stripe to retry
        raise

# You can define a dictionary to map booking_type to handler functions
WEBHOOK_HANDLERS = {
    'hire_booking': {
        'payment_intent.succeeded': handle_hire_booking_succeeded,
        # Add other event types for hire_booking if needed, e.g., 'payment_intent.payment_failed': handle_hire_booking_failed
    },
    # 'service_booking': {
    #     'payment_intent.succeeded': handle_service_booking_succeeded,
    # },
    # Add more booking types and their handlers here
}
