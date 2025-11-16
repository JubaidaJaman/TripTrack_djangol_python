# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, TouristProfileForm, OrganizerProfileForm, EmergencyContactForm
from .models import CustomUser, TouristProfile, OrganizerProfile, EmergencyContact


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Profiles are auto-created by signals, no need to create manually

            # Log the user in
            login(request, user)
            messages.success(request, f'Registration successful! Welcome to UAP TripTrack, {user.username}!')
            return redirect('dashboard')
        else:
            # Form has errors, they will be displayed in template
            messages.error(request, 'Please correct the errors below.')
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


@login_required
def emergency_contacts(request):
    if request.user.user_type != 'tourist':
        messages.error(request, 'Only tourists can manage emergency contacts.')
        return redirect('dashboard')

    contacts = EmergencyContact.objects.filter(user=request.user).order_by('-is_primary', 'full_name')
    primary_contact = contacts.filter(is_primary=True).first()

    return render(request, 'accounts/emergency_contacts.html', {
        'contacts': contacts,
        'primary_contact': primary_contact
    })


@login_required
def add_emergency_contact(request):
    if request.user.user_type != 'tourist':
        messages.error(request, 'Only tourists can add emergency contacts.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, f'Emergency contact {contact.full_name} added successfully!')
            return redirect('emergency_contacts')
    else:
        form = EmergencyContactForm()

    return render(request, 'accounts/add_emergency_contact.html', {'form': form})


@login_required
def edit_emergency_contact(request, contact_id):
    if request.user.user_type != 'tourist':
        messages.error(request, 'Only tourists can edit emergency contacts.')
        return redirect('dashboard')

    contact = get_object_or_404(EmergencyContact, id=contact_id, user=request.user)

    if request.method == 'POST':
        form = EmergencyContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, f'Emergency contact {contact.full_name} updated successfully!')
            return redirect('emergency_contacts')
    else:
        form = EmergencyContactForm(instance=contact)

    return render(request, 'accounts/edit_emergency_contact.html', {'form': form, 'contact': contact})


@login_required
def delete_emergency_contact(request, contact_id):
    if request.user.user_type != 'tourist':
        messages.error(request, 'Only tourists can delete emergency contacts.')
        return redirect('dashboard')

    contact = get_object_or_404(EmergencyContact, id=contact_id, user=request.user)

    if request.method == 'POST':
        contact_name = contact.full_name
        contact.delete()
        messages.success(request, f'Emergency contact {contact_name} deleted successfully!')
        return redirect('emergency_contacts')

    return render(request, 'accounts/delete_emergency_contact.html', {'contact': contact})


@login_required
def set_primary_contact(request, contact_id):
    if request.user.user_type != 'tourist':
        messages.error(request, 'Only tourists can set primary contacts.')
        return redirect('dashboard')

    contact = get_object_or_404(EmergencyContact, id=contact_id, user=request.user)
    contact.is_primary = True
    contact.save()

    messages.success(request, f'{contact.full_name} set as primary emergency contact!')
    return redirect('emergency_contacts')