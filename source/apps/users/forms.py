from django import forms
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from django.utils.translation import gettext_lazy as _

from .models import UserProfile

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    remember = forms.BooleanField(label=_("Remember me"), required=False)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            self.user = authenticate(self.request, username=email, password=password)
            if self.user is None:
                raise forms.ValidationError(_("Invalid e-mail address or password."), code="invalid_login")
            if not self.user.is_active:
                raise forms.ValidationError(_("This account is inactive."), code="inactive")
        return cleaned


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput, strip=False)
    phone = forms.CharField(label=_("Phone"), max_length=20, required=False)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("An account with this e-mail already exists."))
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        password_validation.validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            phone_number=self.cleaned_data.get("phone") or None,
        )


class PasswordResetForm(DjangoPasswordResetForm):
    """Same as Django's, kept here so the template can reference ``form.email``."""


class SetPasswordForm(forms.Form):
    """Password-change form whose field names match templates/auth/password/change.html."""

    password = forms.CharField(label=_("New password"), widget=forms.PasswordInput, strip=False)
    confirm_password = forms.CharField(label=_("Confirm password"), widget=forms.PasswordInput, strip=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        password, confirm = cleaned.get("password"), cleaned.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError(_("The two password fields didn't match."), code="password_mismatch")
        if password:
            password_validation.validate_password(password, self.user)
        return cleaned

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["password"])
        if commit:
            self.user.save(update_fields=["password"])
        return self.user


class ProfileForm(forms.ModelForm):
    bio = forms.CharField(label=_("Bio"), widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "profile_picture")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = getattr(self.instance, "profile", None)
        if profile is not None:
            self.fields["bio"].initial = profile.bio

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("An account with this e-mail already exists."))
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, _created = UserProfile.objects.get_or_create(user=user)
        profile.bio = self.cleaned_data.get("bio") or None
        profile.save(update_fields=["bio"])
        return user
