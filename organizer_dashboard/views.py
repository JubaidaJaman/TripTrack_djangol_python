# organizer_dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Tour
from .forms import TourForm

@login_required
def dashboard(request):
    if request.user.profile.user_type != 'organizer':
        return redirect('home')  # restrict access
    tours = Tour.objects.filter(organizer=request.user).order_by('-created_at')
    return render(request, 'organizer_dashboard/dashboard.html', {'tours': tours})

@login_required
def create_tour(request):
    if request.user.profile.user_type != 'organizer':
        return redirect('home')
    if request.method == 'POST':
        form = TourForm(request.POST)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.organizer = request.user
            tour.save()
            return redirect('organizer_dashboard:dashboard')
    else:
        form = TourForm()
    return render(request, 'organizer_dashboard/create_tour.html', {'form': form})
