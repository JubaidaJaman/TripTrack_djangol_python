from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import uuid
from .models import Tour, UAPDepartment, Booking, Review, Wishlist, Payment
from .forms import TourForm, BookingForm, ReviewForm, UAPDepartmentForm

def home(request):
    # Create UAP departments if none exist
    if UAPDepartment.objects.count() == 0:
        departments_data = [
            {'name': 'Computer Science & Engineering', 'code': 'CSE', 'description': 'Department of Computer Science and Engineering'},
            {'name': 'Electrical & Electronic Engineering', 'code': 'EEE', 'description': 'Department of Electrical and Electronic Engineering'},
            {'name': 'Business Administration', 'code': 'BBA', 'description': 'Department of Business Administration'},
            {'name': 'English', 'code': 'ENG', 'description': 'Department of English'},
            {'name': 'Architecture', 'code': 'ARCH', 'description': 'Department of Architecture'},
            {'name': 'Law', 'code': 'LAW', 'description': 'Department of Law'},
        ]
        for dept_data in departments_data:
            UAPDepartment.objects.create(**dept_data)
    
    # Only show published tours
    featured_tours = Tour.objects.filter(status='published', tour_date__gte=timezone.now())[:8]
    departments = UAPDepartment.objects.all()
    upcoming_tours = Tour.objects.filter(status='published', tour_date__gte=timezone.now()).count()
    
    return render(request, 'home.html', {
        'featured_tours': featured_tours,
        'departments': departments,
        'upcoming_tours': upcoming_tours,
    })

def tour_list(request):
    # Only show published tours
    tours = Tour.objects.filter(status='published', tour_date__gte=timezone.now())
    
    # Filtering
    category = request.GET.get('category')
    department_id = request.GET.get('department')
    price_range = request.GET.get('price_range')
    
    if category:
        tours = tours.filter(category=category)
    if department_id:
        tours = tours.filter(department_id=department_id)
    if price_range:
        if price_range == 'free':
            tours = tours.filter(price=0)
        elif price_range == 'under500':
            tours = tours.filter(price__lte=500)
        elif price_range == '500-1000':
            tours = tours.filter(price__range=(500, 1000))
        elif price_range == 'over1000':
            tours = tours.filter(price__gt=1000)
    
    search = request.GET.get('search')
    if search:
        tours = tours.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(department__name__icontains=search)
        )
    
    departments = UAPDepartment.objects.all()
    categories = Tour.TOUR_CATEGORIES
    
    return render(request, 'tours/tour_list.html', {
        'tours': tours,
        'departments': departments,
        'categories': categories,
    })

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    
    # Allow anyone to view tour details, but restrict booking to published tours only
    if tour.status != 'published' and (not request.user.is_authenticated or request.user != tour.organizer):
        messages.error(request, 'This tour is not available for booking.')
        # Still show the tour details but disable booking
    
    reviews = Review.objects.filter(tour=tour)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()
    
    # Check if user has this tour in wishlist
    in_wishlist = False
    if request.user.is_authenticated and request.user.user_type == 'tourist':
        in_wishlist = Wishlist.objects.filter(tourist=request.user, tour=tour).exists()
    
    if request.method == 'POST' and request.user.is_authenticated:
        if 'add_review' in request.POST:
            # Handle review submission
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            if rating and comment:
                review = Review.objects.create(
                    tour=tour,
                    tourist=request.user,
                    rating=int(rating),
                    comment=comment
                )
                messages.success(request, 'Review added successfully!')
                return redirect('tour_detail', tour_id=tour.id)
        else:
            # Handle booking submission
            if request.user.user_type == 'tourist':
                booking_form = BookingForm(request.POST)
                if booking_form.is_valid():
                    booking = booking_form.save(commit=False)
                    booking.tour = tour
                    booking.tourist = request.user
                    booking.total_price = tour.price * booking.participants
                    
                    # Simulate payment process
                    if booking.payment_method:
                        booking.payment_status = 'paid'
                        booking.status = 'confirmed'
                        booking.transaction_id = f"TXN{str(uuid.uuid4())[:8].upper()}"
                    
                    booking.save()
                    messages.success(request, f'Tour booked successfully! Payment completed via {booking.get_payment_method_display()}.')
                    return redirect('dashboard')
            else:
                messages.error(request, 'Only tourists can book tours.')
    
    else:
        booking_form = BookingForm()
    
    # Get related tours (only published ones)
    related_tours = Tour.objects.filter(
        department=tour.department, 
        status='published',
        tour_date__gte=timezone.now()
    ).exclude(id=tour.id)[:4]
    
    return render(request, 'tours/tour_detail.html', {
        'tour': tour,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': review_count,
        'booking_form': booking_form,
        'in_wishlist': in_wishlist,
        'related_tours': related_tours,
    })

@login_required
def create_tour(request):
    if request.user.user_type != 'organizer':
        messages.error(request, 'Only organizers can create tours.')
        return redirect('home')
    
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.organizer = request.user
            # Tours are created as draft by default
            tour.status = 'draft'
            
            # Auto-assign department from organizer's profile
            from accounts.models import OrganizerProfile
            try:
                organizer_profile = OrganizerProfile.objects.get(user=request.user)
                department, created = UAPDepartment.objects.get_or_create(
                    name=organizer_profile.department,
                    defaults={
                        'code': organizer_profile.department.split()[0],
                        'description': f'{organizer_profile.department} at UAP'
                    }
                )
                tour.department = department
            except OrganizerProfile.DoesNotExist:
                pass
            
            tour.save()
            messages.success(request, 'Tour created successfully! It is now in draft mode. Publish it to make it visible to users.')
            return redirect('dashboard')
    else:
        form = TourForm()
    
    return render(request, 'tours/create_tour.html', {'form': form})

@login_required
def wishlist_toggle(request, tour_id):
    if request.user.user_type != 'tourist':
        return JsonResponse({'error': 'Only tourists can add to wishlist'}, status=403)
    
    tour = get_object_or_404(Tour, id=tour_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        tourist=request.user, 
        tour=tour
    )
    
    if not created:
        wishlist_item.delete()
        return JsonResponse({'added': False, 'message': 'Removed from wishlist'})
    else:
        return JsonResponse({'added': True, 'message': 'Added to wishlist'})

@login_required
def my_wishlist(request):
    if request.user.user_type != 'tourist':
        messages.error(request, 'Only tourists have wishlists.')
        return redirect('home')
    
    wishlist_tours = Tour.objects.filter(
        wishlist__tourist=request.user,
        status='published'
    )
    
    return render(request, 'tours/wishlist.html', {'wishlist_tours': wishlist_tours})

@login_required
def my_reviews(request):
    if request.user.user_type != 'tourist':
        messages.error(request, 'Only tourists can write reviews.')
        return redirect('home')
    
    reviews = Review.objects.filter(tourist=request.user).order_by('-created_at')
    return render(request, 'tours/my_reviews.html', {'reviews': reviews})

def department_tours(request, department_id):
    department = get_object_or_404(UAPDepartment, id=department_id)
    tours = Tour.objects.filter(
        department=department, 
        status='published',
        tour_date__gte=timezone.now()
    )
    
    return render(request, 'tours/department_tours.html', {
        'department': department,
        'tours': tours,
    })