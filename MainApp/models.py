from django.db import models
from django.contrib.auth.models import User




class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    num = models.IntegerField()

    def __str__(self):
        return self.nombre_cliente

class Administrador(models.Model):
    nombre_administrador = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_administrador

class Bodega(models.Model):
    nombre_bodega = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_bodega

class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_categoria

class Producto(models.Model):
    nombre_producto = models.CharField(max_length=255)
    descripcion = models.TextField()
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    bodega = models.ForeignKey('Bodega', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    bodega = models.ForeignKey('Bodega', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    costo = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre_producto

class Compra(models.Model):
    fecha_compra = models.DateField()
    direccion_envio = models.CharField(max_length=255, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_camino', 'En camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
        ('no_entregado', 'No entregado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    TIPO_ENTREGA = [
        ("retiro", "Retiro en tienda"),
        ("envio", "Envío a domicilio"),
    ]
    tipo_entrega = models.CharField(max_length=20, choices=TIPO_ENTREGA, default="envio")
    
    # Campos para gestión de entregas
    delivery_iniciado = models.DateTimeField(null=True, blank=True)
    delivery_finalizado = models.DateTimeField(null=True, blank=True)
    intentos_entrega = models.IntegerField(default=0)
    motivo_no_entrega = models.TextField(blank=True, null=True)
    confirmado_por_cliente = models.BooleanField(default=False)
    fecha_confirmacion_cliente = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Compra {self.id} - Cliente: {self.cliente.nombre_cliente}"

class ProductoCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario_venta = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre_producto} - {self.cantidad} unidades"

class Ingreso(models.Model):
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_ingreso = models.DateField()
    cantidad = models.IntegerField()
    precio_costo = models.IntegerField(default=0)

    def __str__(self):
        return f"Ingreso {self.id} - {self.producto.nombre_producto}"

class Contacto(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField()
    asunto = models.CharField(max_length=255)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.asunto}"
    


class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.user}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre_producto} en carrito {self.cart.id}"
    

class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    buy_order = models.CharField(max_length=100)
    authorization_code = models.CharField(max_length=20)
    accounting_date = models.CharField(max_length=10)
    monto_total = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    productos = models.JSONField()  # Guarda el carrito completo

    def __str__(self):
        return f"Orden {self.buy_order} - {self.usuario.username}"
    

class Boleta(models.Model):
    numero = models.AutoField(primary_key=True)  
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    direccion = models.CharField(max_length=255, default="Pasaje Piedras Negras 9483")
    monto_total = models.IntegerField()


    detalle = models.JSONField()

    def __str__(self):
        return f"Boleta N°{self.numero} - {self.usuario.username}"

class Visita(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visita a {self.producto} en {self.fecha}"


class EntregaDomicilio(models.Model):
    compra = models.OneToOneField(Compra, on_delete=models.CASCADE, related_name='entrega_domicilio')
    inicio_recorrido = models.DateTimeField(null=True, blank=True)
    fin_recorrido = models.DateTimeField(null=True, blank=True)
    intentos_entrega = models.IntegerField(default=0)
    entregado = models.BooleanField(default=False)
    motivo_no_entrega = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Entrega de Pedido #{self.compra.id} - {self.compra.cliente.nombre_cliente}"


class HistorialCambios(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=255)
    detalle = models.TextField()
    TIPOS = [
        ('producto', 'Producto'),
        ('venta', 'Venta'),
        ('entrega', 'Entrega'),
        ('eliminacion', 'Eliminación'),
        ('categoria', 'Categoría'),
        ('bodega', 'Bodega'),
        ('otro', 'Otro'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPOS, default='otro')
    
    class Meta:
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.fecha.strftime('%Y-%m-%d %H:%M')} - {self.usuario.username if self.usuario else 'Usuario eliminado'} - {self.accion}"


class HistorialAdmin(models.Model):
    ACCIONES = [
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('venta_manual', 'Venta Manual'),
        ('inicio_delivery', 'Inicio Delivery'),
        ('fin_delivery', 'Fin Delivery'),
        ('cambio_estado', 'Cambio Estado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.CharField(max_length=50, choices=ACCIONES)
    modelo = models.CharField(max_length=100)  # Ej: "Producto", "Compra", etc
    objeto_id = models.IntegerField(null=True, blank=True)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Historial de Administración'
        verbose_name_plural = 'Historiales de Administración'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.modelo} ({self.fecha.strftime('%Y-%m-%d %H:%M')})"
