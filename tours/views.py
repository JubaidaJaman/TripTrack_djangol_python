# tours/views.py - COMPLETE FIXED VERSION
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.contrib.auth import get_user_model

# Import ALL models from your fixed models.py
from .models import (
    Tour, UAPDepartment, Booking, Review, Wishlist, 
    Payment, Notification, UserNotification
)
from .forms import (
    TourForm, BookingForm, ReviewForm, UAPDepartmentForm, 
    NotificationForm, QuickReminderForm
)

User = get_user_model()

# CORE VIEWS
def home(request):
    featured_tours = Tour.objects.filter(status='published').order_by('-created_at')[:8]
    departments = UAPDepartment.objects.all()[:12]
    upcoming_tours = Tour.objects.filter(
        status='published', 
        tour_date__gt=timezone.now()
    ).count()
    
    context = {
        'featured_tours': featured_tours,
        'departments': departments,
        'upcoming_tours': upcoming_tours,
    }
    return render(request, 'home.html', context)

def tour_list(request):
    tours = Tour.objects.filter(status='published')
    
    # Filtering
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    price_range = request.GET.get('price_range', '')
    sort_by = request.GET.get('sort', 'newest')
    
    if search_query:
        tours = tours.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )
    
    if category_filter:
        tours = tours.filter(category=category_filter)
    
    if price_range == 'free':
        tours = tours.filter(price=0)
    elif price_range == 'under500':
        tours = tours.filter(price__lt=500)
    elif price_range == '500-1000':
        tours = tours.filter(price__range=(500, 1000))
    elif price_range == 'over1000':
        tours = tours.filter(price__gt=1000)
    
    # Sorting
    if sort_by == 'price_low':
        tours = tours.order_by('price')
    elif sort_by == 'price_high':
        tours = tours.order_by('-price')
    elif sort_by == 'date':
        tours = tours.order_by('tour_date')
    else:  # newest
        tours = tours.order_by('-created_at')
    
    # Get user wishlist for template
    user_wishlist = []
    if request.user.is_authenticated and request.user.user_type == 'tourist':
        user_wishlist = Wishlist.objects.filter(tourist=request.user).values_list('tour_id', flat=True)
    
    categories = Tour.CATEGORY_CHOICES
    
    # FIXED: Calculate free tours count properly
    free_tours_count = Tour.objects.filter(status='published', price=0).count()
    
    context = {
        'tours': tours,
        'categories': categories,
        'user_wishlist': user_wishlist,
        'free_tours_count': free_tours_count,  # ADD THIS LINE
    }
    return render(request, 'tours/tour_list.html', context)

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    
    # Check if tour is in user's wishlist
    in_wishlist = False
    if request.user.is_authenticated and request.user.user_type == 'tourist':
        in_wishlist = Wishlist.objects.filter(tourist=request.user, tour=tour).exists()
    
    # Get reviews and average rating
    reviews = Review.objects.filter(tour=tour).order_by('-created_at')
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()
    
    if request.method == 'POST':
        if 'add_review' in request.POST and request.user.is_authenticated and request.user.user_type == 'tourist':
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            
            if rating and comment:
                # Check if user already reviewed this tour
                existing_review = Review.objects.filter(tour=tour, tourist=request.user).first()
                if existing_review:
                    existing_review.rating = rating
                    existing_review.comment = comment
                    existing_review.save()
                    messages.success(request, 'Review updated successfully!')
                else:
                    Review.objects.create(
                        tour=tour,
                        tourist=request.user,
                        rating=rating,
                        comment=comment
                    )
                    messages.success(request, 'Review added successfully!')
                return redirect('tour_detail', tour_id=tour_id)
        
        elif request.user.is_authenticated and request.user.user_type == 'tourist':
            # Handle booking
            participants = request.POST.get('participants', 1)
            payment_method = request.POST.get('payment_method')
            payment_number = request.POST.get('payment_number')
            special_requirements = request.POST.get('special_requirements', '')
            
            try:
                participants = int(participants)
                if participants > tour.available_spots:
                    messages.error(request, f'Only {tour.available_spots} spots available!')
                    return redirect('tour_detail', tour_id=tour_id)
                
                total_price = tour.price * participants
                
                booking = Booking.objects.create(
                    tourist=request.user,
                    tour=tour,
                    participants=participants,
                    total_price=total_price,
                    special_requirements=special_requirements,
                    payment_method=payment_method,
                    payment_number=payment_number,
                    status='confirmed' if tour.price == 0 else 'pending',
                    payment_status='paid' if tour.price == 0 else 'pending'
                )
                
                if tour.price > 0:
                    messages.success(request, 'Booking created! Please complete your payment.')
                else:
                    messages.success(request, 'Booking confirmed successfully!')
                
                return redirect('dashboard')
                
            except ValueError:
                messages.error(request, 'Please enter a valid number of participants.')
    
    context = {
        'tour': tour,
        'in_wishlist': in_wishlist,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': review_count,
    }
    return render(request, 'tours/tour_detail.html', context)

@login_required
def create_tour(request):
    if request.user.user_type != 'organizer':
        messages.error(request, 'Only organizers can create tours.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.organizer = request.user
            
            # Auto-assign department from organizer's profile
            try:
                organizer_profile = request.user.organizerprofile
                tour.department = UAPDepartment.objects.filter(
                    name__icontains=organizer_profile.department
                ).first()
            except:
                pass
            
            tour.save()
            messages.success(request, 'Tour created successfully!')
            return redirect('dashboard')
    else:
        form = TourForm()
    
    return render(request, 'tours/create_tour.html', {'form': form})

@login_required
@require_POST
def wishlist_toggle(request, tour_id):
    if request.user.user_type != 'tourist':
        return JsonResponse({'error': 'Only tourists can use wishlist'}, status=403)
    
    tour = get_object_or_404(Tour, id=tour_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        tourist=request.user,
        tour=tour
    )
    
    if not created:
        wishlist_item.delete()
        return JsonResponse({
            'added': False,
            'message': 'Removed from wishlist'
        })
    
    return JsonResponse({
        'added': True,
        'message': 'Added to wishlist'
    })

@login_required
def my_wishlist(request):
    if request.user.user_type != 'tourist':
        messages.error(request, 'Only tourists can view wishlist.')
        return redirect('dashboard')
    
    wishlist_tours = Tour.objects.filter(
        wishlist__tourist=request.user,
        status='published'
    )
    
    return render(request, 'tours/wishlist.html', {
        'wishlist_tours': wishlist_tours
    })

@login_required
def my_reviews(request):
    if request.user.user_type != 'tourist':
        messages.error(request, 'Only tourists can view reviews.')
        return redirect('dashboard')
    
    reviews = Review.objects.filter(tourist=request.user).order_by('-created_at')
    
    return render(request, 'tours/my_reviews.html', {
        'reviews': reviews
    })

def department_tours(request, department_id):
    department = get_object_or_404(UAPDepartment, id=department_id)
    tours = Tour.objects.filter(
        department=department,
        status='published'
    ).order_by('-created_at')
    
    return render(request, 'tours/department_tours.html', {
        'department': department,
        'tours': tours
    })

@login_required
@require_POST
def generate_qr_code(request, tour_id):
    try:
        tour = get_object_or_404(Tour, id=tour_id)
        
        # Check permission - only organizer or developer can generate QR
        if request.user != tour.organizer and request.user.user_type != 'developer':
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        # Delete old QR code if exists
        if tour.qr_code:
            tour.qr_code.delete(save=False)
        
        # Generate new QR code
        filename = tour.generate_qr_code()
        tour.save()
        
        return JsonResponse({
            'success': True,
            'message': 'QR Code generated successfully!',
            'qr_code_url': tour.qr_code.url
        })
    
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
            notification.is_sent = True
            
            notification.save()
            
            # Get target users and create UserNotification records
            target_users = notification.get_target_users()
            notifications_created = 0
            
            for tourist in target_users:
                UserNotification.objects.get_or_create(
                    user=tourist,
                    notification=notification
                )
                notifications_created += 1
            
            messages.success(request, f'Notification sent to {notifications_created} tourists!')
            return redirect('organizer_notifications')
        else:
            messages.error(request, 'Please correct the errors below.')
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
            
            # Get tourists who booked this tour and create UserNotification records
            target_users = notification.get_target_users()
            notifications_created = 0
            
            for tourist in target_users:
                UserNotification.objects.create(
                    user=tourist,
                    notification=notification
                )
                notifications_created += 1
            
            return JsonResponse({
                'success': True, 
                'message': f'Quick reminder sent to {notifications_created} tourists!'
            })
        
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
    unread_notifications = UserNotification.objects.filter(user=request.user, is_read=False)
    unread_count = unread_notifications.count()
    
    unread_notifications.update(is_read=True, read_at=timezone.now())
    
    messages.success(request, f'Marked {unread_count} notifications as read!')
    return redirect('my_notifications')

@login_required
def get_unread_count(request):
    if request.user.is_authenticated:
        unread_count = UserNotification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'unread_count': unread_count})
    return JsonResponse({'unread_count': 0})

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