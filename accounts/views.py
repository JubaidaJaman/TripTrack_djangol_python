from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse

def home(request):
    return render(request, 'home.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect based on role
            if user.role == 'organizer':
                return redirect('organizer_dashboard:dashboard')
            elif user.role == 'tourist':
                return redirect('tourist_dashboard:dashboard')
            else:
                return redirect('developer_dashboard:dashboard')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'organizer':
                return redirect('organizer_dashboard:dashboard')
            elif user.role == 'tourist':
                return redirect('tourist_dashboard:dashboard')
            else:
                return redirect('developer_dashboard:dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')
