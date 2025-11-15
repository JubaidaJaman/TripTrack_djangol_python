# tours/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.contrib.auth import get_user_model
from .models import Tour, UAPDepartment, Booking, Review, Wishlist, Payment, Notification, UserNotification
from .forms import TourForm, BookingForm, ReviewForm, UAPDepartmentForm, NotificationForm, QuickReminderForm

User = get_user_model()

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
    
    # Auto-generate QR code for published tours if not exists
    if tour.status == 'published' and not tour.qr_code:
        try:
            tour.generate_qr_code()
            tour.save()
        except Exception as e:
            print(f"Error generating QR code: {e}")
    
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

# QR Code View Function
@require_POST
@login_required
def generate_qr_code(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    
    # Check if user is the organizer or developer
    if request.user != tour.organizer and request.user.user_type != 'developer':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        # Delete old QR code if exists
        if tour.qr_code:
            tour.qr_code.delete(save=False)
        
        # Generate new QR code
        tour.generate_qr_code()
        tour.save()
        
        return JsonResponse({'success': True, 'message': 'QR code generated successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# NOTIFICATION VIEWS
@login_required
def send_notification(request):
    if request.user.user_type != 'organizer':
        messages.error(request, 'Only organizers can send notifications.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = NotificationForm(request.POST, organizer=request.user)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.organizer = request.user
            
            # Handle immediate sending
            if not notification.scheduled_send or notification.scheduled_send <= timezone.now():
                notification.is_sent = True
            
            notification.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Create UserNotification records for target users
            if notification.send_to_all_tourists:
                tourists = User.objects.filter(user_type='tourist')
            else:
                tourists = notification.target_users.all()
            
            for tourist in tourists:
                UserNotification.objects.get_or_create(
                    user=tourist,
                    notification=notification
                )
            
            messages.success(request, f'Notification sent to {tourists.count()} tourists!')
            return redirect('organizer_notifications')
    else:
        form = NotificationForm(organizer=request.user)
    
    return render(request, 'notifications/send_notification.html', {'form': form})

@login_required
def send_quick_reminder(request):
    if request.user.user_type != 'organizer':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    if request.method == 'POST':
        tour_id = request.POST.get('tour')
        message = request.POST.get('message')
        
        if not tour_id or not message:
            return JsonResponse({'success': False, 'error': 'Tour and message are required'})
        
        try:
            tour = Tour.objects.get(id=tour_id, organizer=request.user)
            
            # Create notification
            notification = Notification.objects.create(
                organizer=request.user,
                tour=tour,
                title=f'Reminder: {tour.title}',
                message=message,
                notification_type='reminder',
                send_to_all_tourists=False,
                is_sent=True
            )
            
            # Get tourists who booked this tour
            booked_tourists = User.objects.filter(
                booking__tour=tour,
                booking__status='confirmed'
            ).distinct()
            
            notification.target_users.set(booked_tourists)
            
            # Create UserNotification records
            for tourist in booked_tourists:
                UserNotification.objects.create(
                    user=tourist,
                    notification=notification
                )
            
            return JsonResponse({'success': True, 'message': f'Quick reminder sent to {booked_tourists.count()} tourists!'})
        
        except Tour.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Tour not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def organizer_notifications(request):
    if request.user.user_type != 'organizer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    notifications = Notification.objects.filter(organizer=request.user).order_by('-created_at')
    return render(request, 'notifications/organizer_notifications.html', {
        'notifications': notifications
    })

@login_required
def my_notifications(request):
    user_notifications = UserNotification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = user_notifications.filter(is_read=False).count()
    
    return render(request, 'notifications/my_notifications.html', {
        'user_notifications': user_notifications,
        'unread_count': unread_count
    })

@require_POST
@login_required
def mark_notification_read(request, notification_id):
    try:
        user_notification = UserNotification.objects.get(
            id=notification_id,
            user=request.user
        )
        user_notification.mark_as_read()
        return JsonResponse({'success': True})
    except UserNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@login_required
def mark_all_notifications_read(request):
    UserNotification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    messages.success(request, 'All notifications marked as read!')
    return redirect('my_notifications')

@login_required
def get_unread_count(request):
    if request.user.is_authenticated:
        unread_count = UserNotification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'unread_count': unread_count})
    return JsonResponse({'unread_count': 0})

# Helper function to get recent notifications for dropdown
@login_required
def get_recent_notifications(request):
    if request.user.is_authenticated:
        recent_notifications = UserNotification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        notifications_data = []
        for user_notification in recent_notifications:
            notifications_data.append({
                'id': user_notification.id,
                'title': user_notification.notification.title,
                'message': user_notification.notification.message,
                'type': user_notification.notification.notification_type,
                'is_read': user_notification.is_read,
                'created_at': user_notification.created_at.strftime("%b %d, %H:%M"),
                'time_ago': get_time_ago(user_notification.created_at)
            })
        
        return JsonResponse({'notifications': notifications_data})
    return JsonResponse({'notifications': []})

def get_time_ago(created_at):
    """Helper function to get human-readable time difference"""
    now = timezone.now()
    diff = now - created_at
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds // 3600 > 0:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds // 60 > 0:
        return f"{diff.seconds // 60}m ago"
    else:
        return "Just now"