from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, TouristProfileForm, OrganizerProfileForm
from .models import CustomUser, TouristProfile, OrganizerProfile

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create profile based on user type
            if user.user_type == 'tourist':
                TouristProfile.objects.create(user=user)
            elif user.user_type == 'organizer':
                # FIXED: Use default department for organizer
                OrganizerProfile.objects.create(user=user, department='CSE Department')
            
            # Log the user in
            login(request, user)
            messages.success(request, f'Registration successful! Welcome to UAP TripTrack, {user.username}!')
            return redirect('dashboard')
        else:
            return render(request, 'accounts/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

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