from django.shortcuts import render, get_object_or_404, redirect
from tours.models import Booking
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, tourist=request.user)
    if request.method == 'POST':
        method = request.POST.get('method')
        # Mock processing: mark payment_status true and confirm booking
        booking.payment_status = True
        booking.status = 'CONFIRMED'
        booking.save()
        messages.success(request, f"Payment via {method} successful. Booking confirmed.")
        return redirect('tours:detail', pk=booking.tour.id)
    return render(request, 'payments/checkout.html', {'booking': booking})
