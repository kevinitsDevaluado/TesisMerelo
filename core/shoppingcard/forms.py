from django import forms

from core.user.models import *

class UsuarioForm(forms.ModelForm):

    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'dni', 'email'

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': '', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': '', 'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'placeholder': '', 'class': 'form-control'}),
            'email': forms.TextInput(attrs={'placeholder': '', 'class': 'form-control'}),
        }
        