from django.shortcuts import render, get_object_or_404, redirect
from .models import Tour, Booking, Wishlist, Review, Message
from .forms import TourForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

def tour_list(request):
    tours = Tour.objects.filter(date__gte=timezone.now()).order_by('date')
    return render(request, 'tours/list.html', {'tours': tours})

def tour_detail(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    reviews = tour.reviews.all()
    return render(request, 'tours/detail.html', {'tour': tour, 'reviews': reviews})

@login_required
def create_tour(request):
    if not request.user.is_organizer():
        messages.error(request, "Only organizers can create tours.")
        return redirect('tours:list')
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            t = form.save(commit=False)
            t.organizer = request.user
            t.save()
            messages.success(request, "Tour created.")
            return redirect('tours:detail', pk=t.id)
    else:
        form = TourForm()
    return render(request, 'tours/create.html', {'form': form})

@login_required
def wishlist_add(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    Wishlist.objects.get_or_create(tourist=request.user, tour=tour)
    messages.success(request, "Added to wishlist.")
    return redirect('tours:detail', pk=pk)

@login_required
def book_tour(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    # check capacity
    if tour.spots_left() <= 0:
        messages.error(request, "No spots left.")
        return redirect('tours:detail', pk=pk)
    # create booking
    booking = Booking.objects.create(tourist=request.user, tour=tour)
    return redirect('payments:checkout', booking_id=booking.id)

@login_required
def checkin_via_qr(request, pk):
    # this endpoint used when logged in tourist scan QR (the QR points to a URL with tour's uuid)
    tour = get_object_or_404(Tour, pk=pk)
    try:
        booking = Booking.objects.get(tourist=request.user, tour=tour, status='CONFIRMED')
        booking.check_in = True
        booking.save()
        messages.success(request, "Checked in successfully.")
    except Booking.DoesNotExist:
        messages.error(request, "You do not have a confirmed booking for this tour.")
    return redirect('tours:detail', pk=pk)
