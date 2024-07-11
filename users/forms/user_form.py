from django import forms
from django.contrib.auth.forms import UserCreationForm,SetPasswordForm
from ..models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Enter email'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter username'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Enter password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Confirm password'})
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')

class LoginForm(forms.Form):
    email_or_username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter email or Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'}),
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    new_password2 = forms.CharField(
        label="New Password Confirmation",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Enter email'})
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Account with this email does not exist.")
        return email

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        try:
            validate_password(new_password, self.user)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        
        return cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data["new_password"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user