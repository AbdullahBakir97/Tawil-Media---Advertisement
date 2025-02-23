from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 rounded-md bg-tertiary border border-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-md bg-tertiary border border-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-md bg-tertiary border border-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow',
            'placeholder': 'Enter your last name'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-md bg-tertiary border border-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow',
            'placeholder': 'Enter your phone number'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 rounded-md bg-tertiary border border-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 rounded-md bg-tertiary border border-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Use email as username
        if commit:
            user.save()
        return user
