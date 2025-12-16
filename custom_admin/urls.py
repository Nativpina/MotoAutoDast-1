from django.urls import path
from .views import dashboard, admin_login, pagos_view
from django.contrib.auth.views import LogoutView
from MainApp.views import listar_productos, agregar_producto, editar_producto, eliminar_producto

app_name = 'admin'

urlpatterns = [
    path('', admin_login, name="admin_login"),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(), name='admin_logout'),

    path('productos/', listar_productos, name='listar_productos'),
    path('productos/agregar/', agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:producto_id>/', editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),

    path('pagos/', pagos_view, name='pagos'),
]
