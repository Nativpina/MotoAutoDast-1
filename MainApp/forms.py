from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from MainApp.models import Producto, Contacto
from .models import Producto

from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth import get_user_model




class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control mb-3 p-2', 'placeholder': 'Ingresa tu correo electrónico'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control mb-3 p-2',
            'placeholder': 'Ingresa tu nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control mb-3 p-2',
            'placeholder': 'Ingresa tu contraseña'
        })
        self.fields['password1'].help_text = 'Tu contraseña debe tener al menos 8 caracteres y no puede ser completamente numérica.'
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control mb-3 p-2',
            'placeholder': 'Confirma tu contraseña'
        })
        self.fields['password2'].help_text = 'Ingresa la misma contraseña para verificación.'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'descripcion', 'categoria', 'bodega', 'imagen', 'stock', 'costo']

from django import forms
from .models import Contacto

class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre', 'email', 'asunto', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu correo electrónico'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa el asunto'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu mensaje', 'rows': 4}),
        }

User = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        # Renderiza el asunto usando la plantilla `subject_template_name`
        subject = render_to_string(subject_template_name, context).strip()
        body = render_to_string(email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        
        if html_email_template_name:
            html_email = render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='password_reset_email.html',
             html_email_template_name='password_reset_email.html',  # Usa tu plantilla HTML
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, **kwargs):
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            current_site = get_current_site(request) if not domain_override else None
            domain = current_site.domain if current_site else domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': current_site.name if current_site else 'MotoAutoDast',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            self.send_mail(
                subject_template_name, email_template_name,
                context, from_email, user.email,
                html_email_template_name=html_email_template_name
            )

class AddToCartForm(forms.Form):
    producto_id = forms.IntegerField(widget=forms.HiddenInput())
    cantidad = forms.IntegerField(
        min_value=1, 
        initial=1, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px;'})
    )          