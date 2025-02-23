from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone = forms.CharField(required=True)
    interests = forms.MultipleChoiceField(
        choices=[
            (1, 'News & Politics'),
            (2, 'Business & Finance'),
            (3, 'Technology'),
            (4, 'Culture & Arts')
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    accept_terms = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Here you would typically save the interests and phone number
            # to a related profile model
        
        return user
