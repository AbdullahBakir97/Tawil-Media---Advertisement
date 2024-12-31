from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email Address")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Profile Picture")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_verified = models.BooleanField(default=False, verbose_name="Is Verified")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Last Login IP")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date of Birth")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

    def verify_email(self):
        """Mark the user's email as verified."""
        self.is_verified = True
        self.save()

    def deactivate_account(self):
        """Deactivate the user's account."""
        self.is_active = False
        self.save()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="User")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Address")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="City")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Country")
    zip_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="ZIP Code")
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female")],
        blank=True,
        null=True,
        verbose_name="Gender"
    )
    bio = models.TextField(blank=True, null=True, verbose_name="Short Bio")

    def __str__(self):
        return f"Profile of {self.user.username}"

    def update_profile(self, address=None, city=None, country=None, zip_code=None, gender=None, bio=None):
        """Update the user's profile information."""
        if address:
            self.address = address
        if city:
            self.city = city
        if country:
            self.country = country
        if zip_code:
            self.zip_code = zip_code
        if gender:
            self.gender = gender
        if bio:
            self.bio = bio
        self.save()


class UserRole(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Role Name")
    description = models.TextField(blank=True, null=True, verbose_name="Role Description")
    permissions = models.ManyToManyField('auth.Permission', blank=True, related_name="user_roles", verbose_name="Permissions")

    def __str__(self):
        return self.name

    def add_permission(self, permission):
        """Add a permission to the role."""
        self.permissions.add(permission)

    def remove_permission(self, permission):
        """Remove a permission from the role."""
        self.permissions.remove(permission)


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities", verbose_name="User")
    activity_type = models.CharField(max_length=100, verbose_name="Activity Type")
    activity_description = models.TextField(verbose_name="Activity Description")
    ip_address = models.GenericIPAddressField(verbose_name="IP Address")
    activity_date = models.DateTimeField(auto_now_add=True, verbose_name="Activity Date")

    class Meta:
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"
        ordering = ["-activity_date"]

    def __str__(self):
        return f"{self.activity_type} by {self.user.username} on {self.activity_date}"

    def log_activity(self):
        """Log a new user activity."""
        print(f"Activity logged: {self.activity_type} by {self.user.username} at {self.activity_date}")


class PasswordResetRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_requests", verbose_name="User")
    token = models.CharField(max_length=255, unique=True, verbose_name="Reset Token")
    request_date = models.DateTimeField(auto_now_add=True, verbose_name="Request Date")
    expiry_date = models.DateTimeField(verbose_name="Expiry Date")
    is_used = models.BooleanField(default=False, verbose_name="Is Used")
    ip_address = models.GenericIPAddressField(verbose_name="IP Address")

    class Meta:
        verbose_name = "Password Reset Request"
        verbose_name_plural = "Password Reset Requests"
        ordering = ["-request_date"]

    def __str__(self):
        return f"Password reset for {self.user.username} - Token: {self.token[:5]}..."

    def mark_as_used(self):
        """Mark the password reset request as used."""
        self.is_used = True
        self.save()