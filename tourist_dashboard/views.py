# tourist_dashboard/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.contrib import messages
from django import forms

@login_required
def _get_model(app_label, model_name):
    """Try to import a model; return None if not present."""
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None

@login_required
def dashboard(request):
    """
    Dashboard main view. Tries to read Booking, Tour, SavedTour, Profile models if they exist.
    If a model is missing, the template shows fallback messages you can use to adapt.
    """
    user = request.user

    Booking = _get_model('tours', 'Booking') or _get_model('tours', 'Bookings')
    Tour = _get_model('tours', 'Tour') or _get_model('tours', 'Tours')
    SavedTour = _get_model('tours', 'SavedTour') or _get_model('tours', 'Wishlist')

    # default empty lists & stats
    upcoming = []
    past = []
    saved_qs = []
    stats = {'total_bookings': 0, 'total_spent': 0}

    # Safe queries if models exist
    if Booking:
        # try to pick likely fields; if your fields differ, adapt here later
        try:
            today = __import__('datetime').date.today()
            upcoming_qs = Booking.objects.filter(user=user).filter(start_date__gte=today).order_by('start_date')
            past_qs = Booking.objects.filter(user=user).filter(start_date__lt=today).order_by('-start_date')
        except Exception:
            # fallback queries (no date fields)
            upcoming_qs = Booking.objects.filter(user=user).order_by('-id')[:10]
            past_qs = Booking.objects.filter(user=user).order_by('-id')[:10]

        # paginate
        up_p = Paginator(upcoming_qs, 6)
        past_p = Paginator(past_qs, 6)
        upcoming = up_p.get_page(request.GET.get('up_page'))
        past = past_p.get_page(request.GET.get('past_page'))

        stats_agg = Booking.objects.filter(user=user).aggregate(total_bookings=Count('id'), total_spent=Sum('total_price'))
        stats['total_bookings'] = stats_agg.get('total_bookings') or 0
        stats['total_spent'] = stats_agg.get('total_spent') or 0

    if SavedTour:
        saved_qs = SavedTour.objects.filter(user=user).select_related('tour') if hasattr(SavedTour.objects, 'filter') else []
        saved_p = Paginator(saved_qs, 8)
        saved_qs = saved_p.get_page(request.GET.get('saved_page'))

    context = {
        'user': user,
        'booking_model_exists': bool(Booking),
        'tour_model_exists': bool(Tour),
        'saved_model_exists': bool(SavedTour),
        'upcoming_bookings': upcoming,
        'past_bookings': past,
        'saved_tours': saved_qs,
        'stats': stats,
    }
    return render(request, 'tourist_dashboard/dashboard.html', context)


@login_required
def booking_detail(request, booking_id):
    Booking = _get_model('tours', 'Booking') or _get_model('tours', 'Bookings')
    if not Booking:
        messages.error(request, "Booking model not found in your project.")
        return redirect('tourist_dashboard:dashboard')

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'tourist_dashboard/booking_detail.html', {'booking': booking})


# Simple Profile edit form (fallback if you don't have a custom profile form)
class BasicProfileForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)

@login_required
def edit_profile(request):
    Profile = _get_model('accounts', 'Profile') or _get_model('accounts', 'UserProfile')
    user = request.user

    if request.method == 'POST':
        form = BasicProfileForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user.first_name = cd.get('first_name') or user.first_name
            user.last_name = cd.get('last_name') or user.last_name
            if cd.get('email'):
                user.email = cd.get('email')
            user.save()
            messages.success(request, "Profile updated.")
            return redirect('tourist_dashboard:dashboard')
    else:
        initial = {'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email}
        form = BasicProfileForm(initial=initial)

    return render(request, 'tourist_dashboard/edit_profile.html', {'form': form})
