from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from MainApp.models import Producto


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control rounded-pill mb-3 p-3'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'descripcion', 'categoria', 'bodega', 'imagen', 'costo']
