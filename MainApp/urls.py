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
    path('carro/agregar/<int:producto_id>/', views.add_to_cart, name='add_to_cart'),
    path('carro/', views.view_cart, name='view_cart'),
    path('carro/eliminar/<str:key>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('pago/webpay/', views.iniciar_pago, name='iniciar_pago'),
    path('pago/webpay/commit/', views.webpay_commit, name='webpay_commit'),
    path('boleta/<int:boleta_id>/descargar/', views.descargar_boleta, name='descargar_boleta'),
    path('api/recomendar/<int:producto_id>/', views.recomendar_productos, name='recomendar_productos'),
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path("pedido/<int:pedido_id>/", views.detalle_pedido, name="detalle_pedido"),
    path("pedido-detalle/<int:pedido_id>/", views.pedido_detalle, name="pedido_detalle"),


    path('dj-admin/', admin.site.urls),
]