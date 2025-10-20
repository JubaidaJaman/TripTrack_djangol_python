from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from tours.models import Tour, Booking
from accounts.models import User

# Decorator to restrict access to developers only
def developer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'is_developer') or not request.user.is_developer():
            messages.error(request, "Developer access required.")
            return redirect('accounts:developer_login')  # Replace with your login URL name
        return view_func(request, *args, **kwargs)
    return wrapper

# Developer dashboard
@developer_required
def dashboard(request):
    tours = Tour.objects.all().order_by('-created_at')
    users = User.objects.all()
    bookings = Booking.objects.all().order_by('-created_at')[:20]  # latest 20 bookings
    context = {
        'tours': tours,
        'users': users,
        'bookings': bookings
    }
    return render(request, 'developer/dashboard.html', context)

# Toggle active/inactive status of a tour
@developer_required
def tour_toggle_active(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    if hasattr(tour, 'active'):
        tour.active = not tour.active
        tour.save()
        messages.success(request, f"{tour.name} is now {'active' if tour.active else 'inactive'}")
    else:
        messages.error(request, "Tour model does not have an 'active' field.")
    return redirect('developer:dashboard')

# Optional: delete a tour
@developer_required
def tour_delete(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    tour.delete()
    messages.success(request, "Tour deleted successfully.")
    return redirect('developer:dashboard')

# Optional: logout for developer
@login_required
def developer_logout(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:developer_login')  # replace with your login URL
