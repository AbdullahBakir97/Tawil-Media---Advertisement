from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import User, PasswordResetRequest, UserProfile
from .forms import CustomUserCreationForm

# Create your views here.

class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('users:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Log the user in
        login(self.request, user)
        
        # Add success message
        messages.success(self.request, 'Account created successfully! Welcome to Tawil Media.')
        
        return response

@login_required
def dashboard_view(request):
    """User dashboard view."""
    return render(request, 'auth/profile/dashboard.html')

@login_required
def settings_view(request):
    """User settings view."""
    return render(request, 'auth/profile/settings.html', {
        'user': request.user,
        'profile': request.user.profile
    })

@login_required
def profile_view(request):
    """User profile view."""
    return render(request, 'auth/profile/profile.html', {
        'user': request.user,
        'profile': request.user.profile
    })

@require_http_methods(["GET", "POST"])
def password_reset_view(request):
    """Handle password reset requests."""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = get_random_string(64)
            expiry = timezone.now() + timedelta(hours=24)
            
            # Create password reset request
            PasswordResetRequest.objects.create(
                user=user,
                token=token,
                expiry_date=expiry,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # Send reset email
            reset_url = request.build_absolute_uri(
                reverse('users:password_reset_confirm', args=[token])
            )
            send_mail(
                'Reset Your Password',
                f'Click here to reset your password: {reset_url}',
                'noreply@tawilmedia.com',
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset instructions have been sent to your email.')
            return redirect('users:login')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
    
    return render(request, 'auth/password/reset.html')

@require_http_methods(["GET", "POST"])
def password_reset_confirm_view(request, token):
    """Handle password reset confirmation."""
    try:
        reset_request = PasswordResetRequest.objects.get(
            token=token,
            is_used=False,
            expiry_date__gt=timezone.now()
        )
        
        if request.method == 'POST':
            password = request.POST.get('password')
            if password:
                user = reset_request.user
                user.set_password(password)
                user.save()
                
                reset_request.mark_as_used()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('users:login')
        
        return render(request, 'auth/password/change.html')
        
    except PasswordResetRequest.DoesNotExist:
        messages.error(request, 'Invalid or expired password reset link.')
        return redirect('users:password_reset')

@login_required
@require_http_methods(["POST"])
def update_profile_view(request):
    """Update user profile information."""
    user = request.user
    profile = user.profile

    # Update user info
    user.first_name = request.POST.get('first_name', user.first_name)
    user.last_name = request.POST.get('last_name', user.last_name)
    user.email = request.POST.get('email', user.email)
    
    # Handle profile image upload
    if 'profile_image' in request.FILES:
        user.profile_picture = request.FILES['profile_image']
    
    # Update profile info
    profile.bio = request.POST.get('bio', profile.bio)
    
    try:
        user.save()
        profile.save()
        messages.success(request, 'Profile updated successfully.')
    except Exception as e:
        messages.error(request, f'Error updating profile: {str(e)}')
    
    return redirect('users:settings')

@login_required
@require_http_methods(["POST"])
def update_security_view(request):
    """Update security settings."""
    user = request.user
    
    try:
        # Handle 2FA toggle
        two_factor_enabled = request.POST.get('two_factor_enabled') == 'true'
        # Add your 2FA logic here
        
        messages.success(request, 'Security settings updated successfully.')
    except Exception as e:
        messages.error(request, f'Error updating security settings: {str(e)}')
    
    return redirect('users:settings')

@login_required
@require_http_methods(["POST"])
def update_notifications_view(request):
    """Update notification preferences."""
    user = request.user
    
    try:
        # Update notification settings
        # Add your notification settings logic here
        
        messages.success(request, 'Notification preferences updated successfully.')
    except Exception as e:
        messages.error(request, f'Error updating notification preferences: {str(e)}')
    
    return redirect('users:settings')

@login_required
@require_http_methods(["POST"])
def terminate_session_view(request):
    """Terminate a user session."""
    try:
        session_key = request.POST.get('session_key')
        # Add your session termination logic here
        
        messages.success(request, 'Session terminated successfully.')
    except Exception as e:
        messages.error(request, f'Error terminating session: {str(e)}')
    
    return redirect('users:settings')
