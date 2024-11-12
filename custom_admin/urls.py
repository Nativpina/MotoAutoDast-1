from django.urls import path
from .views import dashboard, admin_login
from django.contrib.auth.views import LogoutView
from MainApp.views import listar_productos, agregar_producto


urlpatterns = [
    path('', admin_login, name="admin_login"),  # Página de login
    path('dashboard/', dashboard, name='dashboard'),  # Dashboard del administrador
    path('logout/', LogoutView.as_view(), name='admin_logout'),  # Agrega esta línea
    path('productos/', listar_productos, name='listar_productos'),
    path('productos/agregar/', agregar_producto, name='agregar_producto'),

]
