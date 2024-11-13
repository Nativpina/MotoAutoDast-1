from django.contrib import admin
from django.urls import path, include
from MainApp import views

admin.site.login_template = "admin/Adminlogin.html" 

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('aceites/', views.Aceites, name='lista_aceites'),
    path('accesorios/', views.Accesorios, name='lista_accesorios'),
    path('neumaticos/', views.Neumaticos, name='lista_neumaticos'),
    path('repuestos/', views.Repuestos, name='lista_repuestos'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('producto/<int:id>/', views.producto_detalle, name='producto_detalle'),
    path('registro/', views.registro, name='registro'), 
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('contacto/', views.form_contacto, name='form_contactos'),
    path('ayudaLogin/', views.ayudaLogin, name='ayudaLogin'),
    path('admin/', include('custom_admin.urls')),


    path('dj-admin/', admin.site.urls),
]