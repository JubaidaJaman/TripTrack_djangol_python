# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tours.models import Tour, Booking, Review, UAPDepartment
from accounts.models import CustomUser, TouristProfile, OrganizerProfile
from tours.forms import UAPDepartmentForm

@login_required
def dashboard(request):
    user = request.user
    
    # Ensure user has proper profile
    try:
        if user.user_type == 'tourist':
            profile_obj = TouristProfile.objects.get(user=user)
        elif user.user_type == 'organizer':
            profile_obj = OrganizerProfile.objects.get(user=user)
    except:
        # Create missing profile
        if user.user_type == 'tourist':
            TouristProfile.objects.create(user=user)
        elif user.user_type == 'organizer':
            OrganizerProfile.objects.create(user=user, department='CSE Department')
    
    if user.user_type == 'tourist':
        bookings = Booking.objects.filter(tourist=user).order_by('-booking_date')
        wishlist_count = Tour.objects.filter(wishlist__tourist=user).count()
        reviews_count = Review.objects.filter(tourist=user).count()
        
        context = {
            'bookings': bookings,
            'total_bookings': bookings.count(),
            'upcoming_tours': bookings.filter(status='confirmed').count(),
            'wishlist_count': wishlist_count,
            'reviews_count': reviews_count,
        }
        template = 'dashboard/tourist_dashboard.html'
    
    elif user.user_type == 'organizer':
        tours = Tour.objects.filter(organizer=user).order_by('-created_at')
        bookings = Booking.objects.filter(tour__organizer=user)
        total_revenue = sum(booking.total_price for booking in bookings.filter(status='confirmed'))
        
        # Get organizer profile
        organizer_profile = OrganizerProfile.objects.get(user=user)
        
        # Add publishing AND QR code functionality for organizers
        if request.method == 'POST':
            if 'publish_tour' in request.POST:
                tour_id = request.POST.get('tour_id')
                try:
                    tour_to_publish = Tour.objects.get(id=tour_id, organizer=user)
                    tour_to_publish.status = 'published'
                    tour_to_publish.save()
                    messages.success(request, f'Tour "{tour_to_publish.title}" published successfully!')
                except Tour.DoesNotExist:
                    messages.error(request, 'Tour not found!')
                return redirect('dashboard')
            
            elif 'unpublish_tour' in request.POST:
                tour_id = request.POST.get('tour_id')
                try:
                    tour_to_unpublish = Tour.objects.get(id=tour_id, organizer=user)
                    tour_to_unpublish.status = 'draft'
                    tour_to_unpublish.save()
                    messages.success(request, f'Tour "{tour_to_unpublish.title}" unpublished successfully!')
                except Tour.DoesNotExist:
                    messages.error(request, 'Tour not found!')
                return redirect('dashboard')
            
            # NEW: Handle QR code generation from dashboard
            elif 'generate_qr' in request.POST:
                tour_id = request.POST.get('generate_qr')
                try:
                    tour = Tour.objects.get(id=tour_id, organizer=user)
                    
                    # Delete old QR code if exists
                    if tour.qr_code:
                        tour.qr_code.delete(save=False)
                    
                    # Generate new QR code
                    tour.generate_qr_code()
                    tour.save()
                    
                    messages.success(request, f'QR Code generated for "{tour.title}"! You can now download and share it.')
                except Tour.DoesNotExist:
                    messages.error(request, 'Tour not found!')
                except Exception as e:
                    messages.error(request, f'Error generating QR code: {str(e)}')
                return redirect('dashboard')
        
        context = {
            'tours': tours,
            'bookings': bookings,
            'total_tours': tours.count(),
            'total_bookings': bookings.count(),
            'total_revenue': total_revenue,
            'organizer_profile': organizer_profile,
        }
        template = 'dashboard/organizer_dashboard.html'
    
    elif user.user_type == 'developer':
        users = CustomUser.objects.all().order_by('-date_joined')
        tours = Tour.objects.all().order_by('-created_at')
        bookings = Booking.objects.all()
        departments = UAPDepartment.objects.all()
        
        total_revenue = sum(booking.total_price for booking in bookings.filter(status='confirmed'))
        
        if request.method == 'POST':
            if 'delete_user' in request.POST:
                user_id = request.POST.get('user_id')
                try:
                    user_to_delete = CustomUser.objects.get(id=user_id)
                    if user_to_delete != request.user:
                        user_to_delete.delete()
                        messages.success(request, 'User deleted successfully!')
                    else:
                        messages.error(request, 'You cannot delete your own account!')
                except CustomUser.DoesNotExist:
                    messages.error(request, 'User not found!')
                return redirect('dashboard')
            
            elif 'delete_tour' in request.POST:
                tour_id = request.POST.get('tour_id')
                try:
                    tour_to_delete = Tour.objects.get(id=tour_id)
                    tour_to_delete.delete()
                    messages.success(request, 'Tour deleted successfully!')
                except Tour.DoesNotExist:
                    messages.error(request, 'Tour not found!')
                return redirect('dashboard')
            
            elif 'promote_user' in request.POST:
                user_id = request.POST.get('promote_user')
                try:
                    user_to_promote = CustomUser.objects.get(id=user_id)
                    if user_to_promote != request.user:
                        user_to_promote.user_type = 'developer'
                        user_to_promote.save()
                        messages.success(request, f'{user_to_promote.username} promoted to Developer!')
                    else:
                        messages.error(request, 'You cannot change your own role!')
                except CustomUser.DoesNotExist:
                    messages.error(request, 'User not found!')
                return redirect('dashboard')
            
            # ADD TOUR PUBLISHING FUNCTIONALITY
            elif 'publish_tour' in request.POST:
                tour_id = request.POST.get('tour_id')
                try:
                    tour_to_publish = Tour.objects.get(id=tour_id)
                    tour_to_publish.status = 'published'
                    tour_to_publish.save()
                    messages.success(request, f'Tour "{tour_to_publish.title}" published successfully!')
                except Tour.DoesNotExist:
                    messages.error(request, 'Tour not found!')
                return redirect('dashboard')
            
            elif 'unpublish_tour' in request.POST:
                tour_id = request.POST.get('tour_id')
                try:
                    tour_to_unpublish = Tour.objects.get(id=tour_id)
                    tour_to_unpublish.status = 'draft'
                    tour_to_unpublish.save()
                    messages.success(request, f'Tour "{tour_to_unpublish.title}" unpublished successfully!')
                except Tour.DoesNotExist:
                    messages.error(request, 'Tour not found!')
                return redirect('dashboard')
            
            # NEW: Handle QR code generation for developers
            elif 'generate_qr' in request.POST:
                tour_id = request.POST.get('generate_qr')
                try:
                    tour = Tour.objects.get(id=tour_id)
                    
                    # Delete old QR code if exists
                    if tour.qr_code:
                        tour.qr_code.delete(save=False)
                    
                    # Generate new QR code
                    tour.generate_qr_code()
                    tour.save()
                    
                    messages.success(request, f'QR Code generated for "{tour.title}"!')
                except Tour.DoesNotExist:
                    messages.error(request, 'Tour not found!')
                except Exception as e:
                    messages.error(request, f'Error generating QR code: {str(e)}')
                return redirect('dashboard')
        
        context = {
            'total_users': users.count(),
            'total_tours': tours.count(),
            'total_bookings': bookings.count(),
            'total_departments': departments.count(),
            'total_revenue': total_revenue,
            'recent_users': users[:5],
            'recent_tours': tours[:5],
            'all_users': users,
            'all_tours': tours,
            'all_departments': departments,
        }
        template = 'dashboard/developer_dashboard.html'
    
    return render(request, template, context)

@login_required
def manage_departments(request):
    if request.user.user_type != 'developer':
        messages.error(request, 'Access denied!')
        return redirect('dashboard')
    
    departments = UAPDepartment.objects.all()
    
    if request.method == 'POST':
        form = UAPDepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department added successfully!')
            return redirect('manage_departments')
    else:
        form = UAPDepartmentForm()
    
    return render(request, 'dashboard/manage_departments.html', {
        'departments': departments,
        'form': form
    })