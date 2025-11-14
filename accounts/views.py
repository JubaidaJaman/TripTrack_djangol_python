from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, TouristProfileForm, OrganizerProfileForm
from .models import CustomUser, TouristProfile, OrganizerProfile

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type')
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        
        # Basic validation
        if not username or not email or not password1 or not password2:
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'accounts/register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'accounts/register.html')
        
        # Create user
        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                user_type=user_type,
                phone=phone
            )
            
            # Create profile based on user type
            if user_type == 'tourist':
                TouristProfile.objects.create(user=user)
            elif user_type == 'organizer':
                OrganizerProfile.objects.create(
                    user=user, 
                    department=department or 'CSE Department'
                )
            
            # Log the user in
            login(request, user)
            messages.success(request, f'Registration successful! Welcome to UAP TripTrack, {user.username}!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'accounts/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile(request):
    user = request.user
    
    try:
        if user.user_type == 'tourist':
            profile_obj = TouristProfile.objects.get(user=user)
            ProfileForm = TouristProfileForm
        else:
            profile_obj = OrganizerProfile.objects.get(user=user)
            ProfileForm = OrganizerProfileForm
    except:
        # Create profile if it doesn't exist
        if user.user_type == 'tourist':
            profile_obj = TouristProfile.objects.create(user=user)
            ProfileForm = TouristProfileForm
        else:
            profile_obj = OrganizerProfile.objects.create(user=user, department='CSE Department')
            ProfileForm = OrganizerProfileForm
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile_obj)
    
    return render(request, 'accounts/profile.html', {'form': form, 'user': user})