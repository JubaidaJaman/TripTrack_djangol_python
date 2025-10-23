from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import SignUpForm, LoginForm
from django.contrib.auth.decorators import login_required

def home(request):
    # হোমপেজ দেখাবে সকলকে
    return render(request, 'home.html')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # শুধুমাত্র tourist বা organizer
            if user.role not in ['tourist', 'organizer']:
                return redirect('accounts:signup')
            user.save()
            login(request, user)

            # রিডাইরেক্ট role অনুযায়ী
            if user.role == 'organizer':
                return redirect('organizer_dashboard:dashboard')
            elif user.role == 'tourist':
                return redirect('tour_list')  # tourist tour list page
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
                return redirect('tour_list')  # tourist tour list page
            elif user.role == 'developer':
                return redirect('developer_dashboard:dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

def developer_login_view(request):
    # এখানে login form handle করতে পারো, অথবা সরাসরি redirect করতে পারো
    return render(request, 'accounts/developer_login.html')

@login_required
def developer_dashboard_view(request):
    organizer_news = "এখানে সব organizer related news দেখাবে।"
    tour_news = "এখানে সব tour related news দেখাবে।"
    context = {
        'organizer_news': organizer_news,
        'tour_news': tour_news,
    }
    return render(request, 'accounts/developer_dashboard.html', context)

def developer_dashboard_view(request):
    if not request.user.is_authenticated or request.user.role != 'developer':
        return redirect('accounts:login')
    # এখানে তুমি organizer/tour news নিয়ে template এ পাঠাতে পারো
    context = {
        'organizer_news': "Sample news about organizers",
        'tour_news': "Sample news about tours"
    }
    return render(request, 'accounts/developer_dashboard.html', context)
