from django.urls import path
from .views import dashboard, admin_login
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', admin_login, name="admin_login"),  # Página de login
    path('dashboard/', dashboard, name='dashboard'),  # Dashboard del administrador
    path('logout/', LogoutView.as_view(), name='admin_logout'),  # Agrega esta línea

]
