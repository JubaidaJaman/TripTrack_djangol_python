# organizer_dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import OrganizerTourForm
from tours.models import Tour

def organizer_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # or your login URL name
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'organizer':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    _wrapped.__name__ = view_func.__name__
    return _wrapped

@organizer_required
def dashboard(request):
    # list of organizer's tours
    tours = Tour.objects.filter(organizer=request.user).order_by('-created_at')
    return render(request, 'organizer_dashboard/dashboard.html', {'tours': tours})

@organizer_required
def create_tour(request):
    if request.method == 'POST':
        form = OrganizerTourForm(request.POST, request.FILES)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.organizer = request.user
            # ensure available seats set
            tour.available_seats = tour.total_seats
            tour.save()
            return redirect('organizer_dashboard')
    else:
        form = OrganizerTourForm()
    return render(request, 'organizer_dashboard/create_tour.html', {'form': form})

@organizer_required
def edit_tour(request, pk):
    tour = get_object_or_404(Tour, pk=pk, organizer=request.user)
    if request.method == 'POST':
        form = OrganizerTourForm(request.POST, request.FILES, instance=tour)
        if form.is_valid():
            form.save()
            return redirect('organizer_dashboard')
    else:
        form = OrganizerTourForm(instance=tour)
    return render(request, 'organizer_dashboard/create_tour.html', {'form': form, 'tour': tour})

@organizer_required
def delete_tour(request, pk):
    tour = get_object_or_404(Tour, pk=pk, organizer=request.user)
    if request.method == 'POST':
        tour.delete()
        return redirect('organizer_dashboard')
    return render(request, 'organizer_dashboard/confirm_delete.html', {'tour': tour})
