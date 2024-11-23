from django import forms
from django.core import validators
from app.models import *
import datetime
import re

class registroUser(forms.ModelForm): #Registro user para iniciar sesion
    class Meta:
        model = User
        fields = ('username','password','email','first_name','last_name')

        widgets = {
            'username' : forms.TextInput(attrs={'class':'form-control'}),
            'password' : forms.PasswordInput(attrs={'class':'form-control'}),
            'email' : forms.EmailInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name' : forms.TextInput(attrs={'class':'form-control'}),
        }
        
class registroUsuario(forms.ModelForm): #Registro Usuario/Empleado
    class Meta:
        model = Usuario 
        fields = ('rut','telefono') 

        widgets = {
            'rut' : forms.TextInput(attrs={'class':'form-control'}),
            'telefono' : forms.NumberInput(attrs={'class':'form-control'}),
        }


## Para registar vehiculo
class registroVehiculo(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ('patente', 'modelo', 'marca', 'anno','conductor')

        widgets = {
            'patente' : forms.TextInput(attrs={'class':'form-control'}),
            'modelo' : forms.TextInput(attrs={'class':'form-control'}),
            'marca' : forms.TextInput(attrs={'class':'form-control'}),
            'anno' : forms.NumberInput(attrs={'class':'form-control'}),
            'conductor':forms.Select(attrs={'class':'form-select'}),
        }
        
    def clean_patente(self):
        patente = self.cleaned_data.get('patente')
        if not re.match(r'^[A-Z0-9]{6}$', patente):
            raise forms.ValidationError('La patente debe tener 6 caracteres alfanuméricos en mayúsculas.')
        return patente
    
class crearGPS(forms.ModelForm):
    class Meta:
        model = GPSLog
        fields = ('latitud','longitud')
