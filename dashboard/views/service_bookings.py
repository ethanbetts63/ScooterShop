# service_bookings.py
import calendar
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test # Import user_passes_test
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

from service.models import ServiceBooking, ServiceType # Ensure your model path is correct
from dashboard.models import BlockedServiceDate # Corrected import

# REMOVE the is_staff_check function definition here

# View for the service bookings list page
@user_passes_test(lambda u: u.is_staff) # Use lambda directly
def service_bookings_view(request):
    bookings = ServiceBooking.objects.all().order_by('-appointment_date')

    context = {
        'page_title': 'Manage Service Bookings',
        'bookings': bookings,
    }
    return render(request, 'dashboard/service_bookings.html', context) # Make sure this template name is correct

# View for displaying details of a single service booking
@user_passes_test(lambda u: u.is_staff) # Use lambda directly
def service_booking_details_view(request, pk):
    booking = get_object_or_404(ServiceBooking, pk=pk)

    context = {
        'page_title': f'Service Booking Details - {booking.id}',
        'booking': booking,
    }
    return render(request, 'dashboard/service_booking_details.html', context) # Make sure this template name is correct

# Returns service bookings and blocked dates as a JSON feed for FullCalendar
@user_passes_test(lambda u: u.is_staff) # Use lambda directly
def get_service_bookings_json(request):
    start_param = request.GET.get('start')
    end_param = request.GET.get('end')

    bookings = ServiceBooking.objects.all()
    blocked_service_dates = BlockedServiceDate.objects.all() # Fetch all blocked dates initially

    start_date = None
    end_date = None

    # Filter bookings and blocked dates by the date range FullCalendar requests
    if start_param and end_param:
        try:
            start_date = parse_datetime(start_param)
            end_date = parse_datetime(end_param)

            if start_date and end_date:
                bookings = bookings.filter(
                    appointment_date__gte=start_date,
                    appointment_date__lt=end_date # Use lt for end date as FullCalendar end is exclusive
                )
                # Filter blocked dates that overlap with the requested range
                blocked_service_dates = blocked_service_dates.filter(
                    start_date__lte=end_date.date(), # Compare date parts
                    end_date__gte=start_date.date()  # Compare date parts
                )


        except (ValueError, TypeError):
            pass # Handle potential parsing errors


    events = []
    # Add booking events
    for booking in bookings:
        # Prepare the data in FullCalendar's Event Object format
        event_title = f"{booking.customer_name or 'Anonymous'} - {booking.service_type.name}"

        # Prepare extendedProps for custom rendering
        extended_props = {
            'customer_name': booking.customer_name or 'Anonymous',
            'service_type': booking.service_type.name,
            'status': booking.status,
            # Add vehicle details, checking if they exist
            'vehicle_make': getattr(booking, 'anon_vehicle_make', None) or (getattr(booking.vehicle, 'make', None) if hasattr(booking, 'vehicle') and booking.vehicle else None) or '',
            'vehicle_model': getattr(booking, 'anon_vehicle_model', None) or (getattr(booking.vehicle, 'model', None) if hasattr(booking, 'vehicle') and booking.vehicle else None) or '',
            'booking_id': booking.pk,
        }

        event = {
            'id': booking.pk,
            'title': event_title, # Standard FullCalendar title (can be used by list view, etc.)
            'start': booking.appointment_date.isoformat(),
            'url': reverse('dashboard:service_booking_details', args=[booking.pk]), # URL for event click
            'extendedProps': extended_props, # Custom data for our eventContent callback
        }
        events.append(event)

    # Add blocked date events as regular events with a specific property and class
    for blocked_service_date_range in blocked_service_dates:
        current_date = blocked_service_date_range.start_date
        # Ensure end_date is included by adding one day for iteration comparison
        while current_date <= blocked_service_date_range.end_date:
            blocked_event = {
                'start': current_date.isoformat(),
                'title': 'Blocked Day', # Title for the tile
                'extendedProps': {
                    'is_blocked': True, # Custom property to identify blocked dates
                    'description': blocked_service_date_range.description, # Include description
                },
                'className': 'blocked-date-tile', # Custom class for styling
                'display': 'block', # Ensure it's treated as a regular event
            }
            events.append(blocked_event)
            current_date += timedelta(days=1)


    return JsonResponse(events, safe=False)

# View for the service booking search page
@user_passes_test(lambda u: u.is_staff) # Use lambda directly
def service_booking_search_view(request):
    query = request.GET.get('q')
    # Default sort matches the default option value in the template
    sort_by = request.GET.get('sort_by', '-appointment_date')

    # Get all possible status choices from the model
    booking_statuses = ServiceBooking.STATUS_CHOICES
    all_status_values = [status[0] for status in booking_statuses]

    # Determine the selected statuses
    # If 'status' is not in GET parameters, it's likely the initial load,
    # so select all statuses by default. Otherwise, get the list of selected statuses.
    if 'status' not in request.GET:
        selected_statuses = all_status_values
    else:
        selected_statuses = request.GET.getlist('status')


    bookings = ServiceBooking.objects.all()

    # --- Filtering by Status ---
    if selected_statuses:
        bookings = bookings.filter(status__in=selected_statuses)

    # --- Filtering by Search Query ---
    if query:
        # Start with an empty Q object for filtering
        search_filter = Q()

        # Add text field searches (case-insensitive contains)
        search_filter |= Q(customer_name__icontains=query)
        search_filter |= Q(customer_email__icontains=query)
        search_filter |= Q(customer_phone__icontains=query)
        search_filter |= Q(customer_address__icontains=query)
        search_filter |= Q(service_type__name__icontains=query)
        search_filter |= Q(customer_notes__icontains=query)
        search_filter |= Q(mechanic_notes__icontains=query)
        search_filter |= Q(anon_vehicle_make__icontains=query)
        search_filter |= Q(anon_vehicle_model__icontains=query)
        search_filter |= Q(anon_vehicle_vin_number__icontains=query)
        search_filter |= Q(anon_engine_number__icontains=query)
        search_filter |= Q(anon_vehicle_rego__icontains=query)
        search_filter |= Q(anon_vehicle_transmission__icontains=query)
        search_filter |= Q(booking_reference__icontains=query)

        bookings = bookings.filter(search_filter)

    # --- Sorting ---
    # Apply sorting based on values from the template
    if sort_by == 'id':
        bookings = bookings.order_by('id')
    elif sort_by == '-id':
        bookings = bookings.order_by('-id')
    elif sort_by == 'appointment_date':
        bookings = bookings.order_by('appointment_date')
    elif sort_by == '-appointment_date': # Default
        bookings = bookings.order_by('-appointment_date')
    elif sort_by == 'date_created':
        bookings = bookings.order_by('created_at')
    elif sort_by == '-date_created':
        bookings = bookings.order_by('-created_at')
    # No need for an else here, as sort_by has a default value

    context = {
        'page_title': 'Service Booking Search',
        'bookings': bookings,
        'query': query,
        'sort_by': sort_by,
        'selected_statuses': selected_statuses,
        'booking_statuses': booking_statuses,
    }
    return render(request, 'dashboard/service_booking_search.html', context) # Make sure this template name is correct