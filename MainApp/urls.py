from django.urls import path, include
from MainApp import views



urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('categoria/<str:nombre_categoria>/', views.productos_por_categoria, name='productos_categoria'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login-redirect/', views.custom_login_redirect, name='login_redirect'),
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

]
