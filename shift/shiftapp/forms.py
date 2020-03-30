from django import forms
from django.shortcuts import redirect
 
class ResetForm(forms.Form):
    reset = forms.CharField()
