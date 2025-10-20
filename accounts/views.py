from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm
from django.contrib import messages
from .models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.utils import timezone
from tours.models import Tour

def home(request):
    # homepage view will be in project-level templates; import tours to show upcoming events via context processors or call model
    from tours.models import Tour
    upcoming = Tour.objects.filter(date__gte=timezone.now()).order_by('date')[:6]
    return render(request, 'home.html', {'upcoming': upcoming})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # set role provided by user in form
            user.role = form.cleaned_data['role']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()
            messages.success(request, "Account created. Please login.")
            return redirect('accounts:login')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

# developer login view (separate)
from django.contrib.auth.forms import AuthenticationForm
def developer_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_developer():
                login(request, user)
                return redirect('developer:dashboard')
            else:
                messages.error(request, "Not a developer.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/developer_login.html', {'form': form})

# Use Django default login/logout (we'll add urls)
