from django.urls import path
from .views import dashboard, admin_login
from django.contrib.auth.views import LogoutView
from MainApp.views import listar_productos, agregar_producto, editar_producto, eliminar_producto, lista_contactos, ajustes


urlpatterns = [
    path('', admin_login, name="admin_login"),  # Página de login
    path('dashboard/', dashboard, name='dashboard'),  # Dashboard del administrador
    path('logout/', LogoutView.as_view(), name='admin_logout'),  # Agrega esta línea
    path('productos/', listar_productos, name='listar_productos'),
    path('productos/agregar/', agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:producto_id>/', editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),
    path('contactos/', lista_contactos, name='lista_contactos'),
    path('ajustes/', ajustes, name='ajustes'),

]
