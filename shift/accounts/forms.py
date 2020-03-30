from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class LoginForm(AuthenticationForm):
    """ログインフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("name", "gender",)
        
class DaysForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("days", "days_late",)

        

        
