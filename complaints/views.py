from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import RegisterForm, UserProfileForm, ProfileForm, ComplaintForm, LoginForm
from .models import Profile, Complaint
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

@never_cache
def index(request):
    return render(request, 'complaints/index.html')

@never_cache
def about(request):
    return render(request, 'complaints/about.html')

@never_cache
def custom_login(request):
    return render(request, 'complaints/login.html')

@never_cache
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('student_login')
    else:
        form = RegisterForm()
    return render(request, 'complaints/register.html', {'form': form})

@never_cache
def student_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            if not User.objects.filter(username=username).exists():
                messages.error(request, 'User not found. Please register first.')
                return redirect('student_login')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if request.user.is_authenticated:
                    auth_logout(request)
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('student_login')
    else:
        form = LoginForm()
    return render(request, 'complaints/student_login.html', {'form': form})

@never_cache
@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(request, 'complaints/dashboard2.html', {
            'total_complaints': 0,
            'in_progress_complaints': 0,
            'resolved_complaints': 0,
            'profile': None
        })
    
    profile = request.user.profile
    total_complaints = Complaint.objects.filter(user=request.user).count()
    in_progress_complaints = Complaint.objects.filter(user=request.user, status='In progress').count()
    resolved_complaints = Complaint.objects.filter(user=request.user, status='Resolved').count()

    context = {
        'profile': profile,
        'total_complaints': total_complaints,
        'in_progress_complaints': in_progress_complaints,
        'resolved_complaints': resolved_complaints,
    }
    return render(request, 'complaints/dashboard2.html', context)

@never_cache
@login_required
def lodge_complaint(request):
    if request.user.is_superuser:
        return render(request, 'complaints/lodge_complaint2.html', {'form': None})

    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            if request.FILES.get('file'):
                complaint.file = request.FILES['file']
            complaint.save()
            messages.success(request, 'Complaint lodged successfully!')
            return redirect('lodge_complaint')
        else:
            messages.error(request, 'Failed to lodge the complaint. Please check the form and try again.')
            return redirect('lodge_complaint')
    else:
        form = ComplaintForm()
    return render(request, 'complaints/lodge_complaint2.html', {'form': form})

@never_cache
@login_required
def complaint_history(request):
    if request.user.is_superuser:
        return render(request, 'complaints/complaint_history2.html', {
            'complaints': None,
            'status_choices': Complaint.STATUS_CHOICES,
            'status_filter': None
        })

    complaints = Complaint.objects.filter(user=request.user)
    status_filter = request.GET.get('status')
    if status_filter:
        complaints = complaints.filter(status=status_filter)

    context = {
        'complaints': complaints,
        'status_choices': Complaint.STATUS_CHOICES,
        'status_filter': status_filter,
    }
    return render(request, 'complaints/complaint_history2.html', context)

@never_cache
@login_required
def profile(request):
    if request.user.is_superuser:
        return render(request, 'complaints/profile2.html', {
            'user_form': None,
            'profile_form': None
        })

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            if profile_form.cleaned_data['year_of_study'] == '':
                profile.year_of_study = None
            profile.save()
            return redirect('dashboard')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'complaints/profile2.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@never_cache
def password_reset_form(request):
    return render(request, 'complaints/password_reset_form.html')

@never_cache
@login_required
def password_reset(request):
    if request.user.is_superuser:
        return render(request, 'complaints/password_reset2.html')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user
        if not check_password(current_password, user.password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif not is_password_complex(new_password):
            messages.error(request, 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character.')
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password reset successful!')
            return render(request, 'complaints/password_reset2.html')

    return render(request, 'complaints/password_reset2.html')

def is_password_complex(password):
    if len(password) < 8:
        return False
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?/' for char in password)
    return has_upper and has_lower and has_digit and has_special

@never_cache
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')  # Redirect to homepage or another page after logout





