from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, F
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import Compra, ProductoCompra, Boleta
from .models import (
    Producto, Categoria, Bodega, Contacto, Cliente, Compra,
    ProductoCompra, Orden, Boleta, Visita
)

from .forms import CustomUserCreationForm, AddToCartForm, ProductoForm, ContactoForm

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys

from django.views.decorators.csrf import csrf_exempt


# ================================
#  INICIO Y CATÁLOGO
# ================================

def inicio(request):
    productos = Producto.objects.filter(stock__gt=0)
    return render(request, 'inicio.html', {'productos': productos})


def lista_productos(request):
    productos = Producto.objects.filter(stock__gt=0)
    return render(request, 'catalogoTest.html', {'productos': productos})


def productos_por_categoria(request, nombre_categoria):
    categoria = Categoria.objects.filter(nombre_categoria=nombre_categoria).first()
    productos = Producto.objects.filter(categoria=categoria, stock__gt=0) if categoria else []
    return render(request, 'catalogo.html', {'productos': productos, 'categoria': nombre_categoria})


Aceites = lambda r: productos_por_categoria(r, "Aceite")
Accesorios = lambda r: productos_por_categoria(r, "Accesorios")
Neumaticos = lambda r: productos_por_categoria(r, "Neumaticos")
Repuestos = lambda r: productos_por_categoria(r, "Repuestos")


def producto_detalle(request, id):
    producto = get_object_or_404(Producto, id=id)
    form = AddToCartForm(initial={'producto_id': producto.id})
    return render(request, 'producto_detalle.html', {'producto': producto, 'form': form})


# ================================
#  REGISTRO Y LOGIN
# ================================

def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')

    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/registro.html', {'form': form})


# ================================
#  BUSCAR PRODUCTOS
# ================================

def buscar_productos(request):
    query = request.GET.get('q', '')
    productos = Producto.objects.filter(
        nombre_producto__icontains=query,
        stock__gt=0
    ) if query else []

    return render(request, 'busqueda.html', {
        'productos': productos,
        'categoria': f"Resultados para '{query}'" if query else "Sin resultados"
    })


# ================================
#  CRUD PRODUCTOS (solo admin)
# ================================

def listar_productos(request):
    if not request.user.is_superuser:
        return redirect('/')
    return render(request, 'admin/productos.html', {'productos': Producto.objects.all()})


def agregar_producto(request):
    if not request.user.is_superuser:
        return redirect('/')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin:listar_productos')
    else:
        form = ProductoForm()

    # Pasar categorías y bodegas al template
    categorias = Categoria.objects.all()
    bodegas = Bodega.objects.all()

    return render(request, 'admin/agregar_producto.html', {
        'form': form,
        'categorias': categorias,
        'bodegas': bodegas
    })


def editar_producto(request, producto_id):
    if not request.user.is_superuser:
        return redirect('/')

    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')

    else:
        form = ProductoForm(instance=producto)

    return render(request, 'admin/editar_producto.html', {'form': form, 'producto': producto})


def eliminar_producto(request, producto_id):
    if not request.user.is_superuser:
        return redirect('/')

    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        producto.delete()
        return redirect('admin:listar_productos')

    return render(request, 'admin/confirmar_eliminacion.html', {'producto': producto})


# ================================
#  CATEGORÍAS Y BODEGAS (Admin)
# ================================

def agregar_categoria(request):
    if not request.user.is_superuser:
        return redirect('/')

    if request.method == 'POST':
        nombre = request.POST.get('nombre_categoria', '').strip()
        if nombre:
            Categoria.objects.create(nombre_categoria=nombre)
            messages.success(request, f'Categoría "{nombre}" creada exitosamente.')
            return redirect('admin:agregar_producto')
        else:
            messages.error(request, 'El nombre de la categoría no puede estar vacío.')

    return render(request, 'admin/agregar_categoria.html')


def agregar_bodega(request):
    if not request.user.is_superuser:
        return redirect('/')

    if request.method == 'POST':
        nombre = request.POST.get('nombre_bodega', '').strip()
        if nombre:
            Bodega.objects.create(nombre_bodega=nombre)
            messages.success(request, f'Bodega "{nombre}" creada exitosamente.')
            return redirect('admin:agregar_producto')
        else:
            messages.error(request, 'El nombre de la bodega no puede estar vacío.')

    return render(request, 'admin/agregar_bodega.html')


# ================================
#  CONTACTO
# ================================

def form_contacto(request):
    form = ContactoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('lista_contactos')

    return render(request, 'contacto.html', {'form': form})


def lista_contactos(request):
    if not request.user.is_superuser:
        return redirect('/')
    return render(request, 'admin/listaContacto.html', {'contactos': Contacto.objects.all()})




def add_to_cart(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})

    # Obtener cantidad del formulario
    cantidad = int(request.POST.get('cantidad', 1))

    # 🔥 PREVENIR cantidades negativas o cero
    if cantidad < 1:
        cantidad = 1

    # 🔥 PREVENIR que agreguen más stock del disponible
    if cantidad > producto.stock:
        cantidad = producto.stock

    carrito[str(producto_id)] = {
        'nombre': producto.nombre_producto,
        'precio': producto.costo,
        'cantidad': cantidad,
    }

    request.session['carrito'] = carrito
    messages.success(request, 'Producto añadido al carrito.')

    return redirect('view_cart')

def view_cart(request):
    carrito = request.session.get('carrito', {})
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return render(request, 'carro.html', {'carrito': carrito, 'total': total})


def remove_from_cart(request, key):
    carrito = request.session.get('carrito', {})
    carrito.pop(key, None)
    request.session['carrito'] = carrito
    return redirect('view_cart')


def checkout(request):
    carrito = request.session.get('carrito', {})
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return render(request, 'checkout.html', {'carrito': carrito, 'total': total})




@login_required
def iniciar_pago(request):

    # 👉 Recibir datos del formulario
    if request.method == "POST":
        tipo_entrega = request.POST.get("envio_opcion", "retiro")
        direccion_envio = request.POST.get("direccion_envio", "")

        # Guardamos temporalmente en sesión
        request.session["tipo_entrega"] = tipo_entrega
        request.session["direccion_envio"] = direccion_envio

    carrito = request.session.get('carrito', {})
    total = sum(float(i['precio']) * int(i['cantidad']) for i in carrito.values())

    if total <= 0:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('view_cart')

    # Guardar carrito para Webpay
    request.session["carrito_pago"] = carrito.copy()

    # Webpay data
    buy_order = f"O-{request.user.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    session_id = str(request.user.id)
    return_url = request.build_absolute_uri(reverse('webpay_commit'))

    tx = Transaction(WebpayOptions(
        IntegrationCommerceCodes.WEBPAY_PLUS,
        IntegrationApiKeys.WEBPAY,
        IntegrationType.TEST
    ))

    response = tx.create(buy_order, session_id, int(total), return_url)

    return render(request, "webpay_redirect.html", {
        "url_webpay": response["url"],
        "token": response["token"]
    })



@csrf_exempt
def webpay_commit(request):
    token = request.POST.get("token_ws") or request.GET.get("token_ws")
    tbk = request.POST.get("TBK_TOKEN")

    # 🔹 Si Webpay devuelve TBK sin token → pago cancelado
    if tbk and not token:
        messages.error(request, "Pago cancelado.")
        return redirect("checkout")

    # 🔹 Si no hay token → error
    if not token:
        messages.error(request, "Error en transacción.")
        return redirect("checkout")

    # Configuración Webpay
    tx = Transaction(WebpayOptions(
        IntegrationCommerceCodes.WEBPAY_PLUS,
        IntegrationApiKeys.WEBPAY,
        IntegrationType.TEST
    ))

    result = tx.commit(token)

    # 🔹 Si el pago no fue autorizado
    if result["status"] != "AUTHORIZED":
        messages.error(request, "Pago rechazado.")
        return redirect("checkout")

    # 🔹 Datos del carrito guardados para el pago
    carrito_original = request.session.get("carrito_pago", {}).copy()

    # 🔹 Crear cliente si no existe
    cliente, _ = Cliente.objects.get_or_create(
        user=request.user,
        defaults={
            'nombre_cliente': request.user.username,
            'email': request.user.email
        }
    )

    # 🔹 Crear la compra y los detalles dentro de una transacción
    with transaction.atomic():

        compra = Compra.objects.create(
            fecha_compra=timezone.now(),
            cliente=cliente,
            estado="pendiente",
            monto=result["amount"],
            tipo_entrega=request.session.get("tipo_entrega", "retiro"),
            direccion_envio=request.session.get("direccion_envio", "")
        )

        detalle = []

        # 🔹 Registrar cada producto del carrito
        for key, item in carrito_original.items():
            producto = Producto.objects.get(id=int(key))

            # Verificar stock
            if producto.stock < item["cantidad"]:
                raise ValueError("Stock insuficiente.")

            ProductoCompra.objects.create(
                compra=compra,
                producto=producto,
                cantidad=item["cantidad"],
                precio_unitario_venta=item["precio"]
            )

            # Descontar stock
            producto.stock = F("stock") - item["cantidad"]
            producto.save()

            # Detalle para la boleta
            detalle.append({
                "producto": item["nombre"],
                "cantidad": item["cantidad"],
                "precio": item["precio"],
            })

        # 🔹 Registrar orden
        orden = Orden.objects.create(
            usuario=request.user,
            buy_order=result["buy_order"],
            authorization_code=result["authorization_code"],
            monto_total=result["amount"],
            productos=carrito_original
        )

        # 🔹 Crear boleta
        boleta = Boleta.objects.create(
            usuario=request.user,
            monto_total=result["amount"],
            direccion="Pasaje Piedras Negras 9483",
            detalle=detalle
        )

        # 🔹 Enviar correo SOLO si corresponde
        if compra.tipo_entrega != "retiro":
            enviar_correo_confirmacion_pedido(compra)

        # 🔹 Limpiar sesiones
        request.session["carrito"] = {}
        request.session["carrito_pago"] = {}
        request.session.pop("tipo_entrega", None)
        request.session.pop("direccion_envio", None)

    # 🔹 Mostrar página de éxito
    return render(request, "webpay_exito.html", {
        "result": result,
        "carrito": carrito_original,
        "total": result["amount"],
        "orden": orden,
        "boleta": boleta,
        "es_retiro": compra.tipo_entrega == "retiro",
    })






def enviar_correo_confirmacion_pedido(compra):
    cliente = compra.cliente
    usuario = cliente.user

    asunto = f"Confirmación de tu pedido #{compra.id} – MotoAutoDast"

    contexto = {'cliente': cliente, 'compra': compra}

    html = render_to_string('emails/confirmacion_pedido.html', contexto)
    texto_plano = strip_tags(html)

    send_mail(
        asunto,
        texto_plano,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        html_message=html,
        fail_silently=False,
    )


# ================================
#  MIS PEDIDOS
# ================================

@login_required
def mis_pedidos(request):
    cliente = Cliente.objects.filter(user=request.user).first()

    if not cliente:
        messages.error(request, "Tu cuenta no está asociada a un cliente.")
        return redirect('inicio')

    pedidos = Compra.objects.filter(cliente=cliente).order_by('-fecha_compra')
    return render(request, 'mis_pedidos.html', {'pedidos': pedidos})


@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Compra, id=pedido_id, cliente__user=request.user)
    productos = ProductoCompra.objects.filter(compra=pedido)

    return render(request, "detalle_pedido.html", {
        "pedido": pedido,
        "productos": productos,
    })


# ================================
#  RECOMENDACIONES
# ================================

def recomendar_productos(request, producto_id):
    producto = Producto.objects.filter(id=producto_id).first()
    if not producto:
        return JsonResponse({"recomendaciones": []})

    similares = Producto.objects.filter(
        categoria=producto.categoria
    ).exclude(id=producto.id).annotate(
        total_visitas=Count("visita")
    ).order_by("-total_visitas")[:4]

    data = [{
        "id": p.id,
        "nombre": p.nombre_producto,
        "descripcion": p.descripcion[:80] + "..." if len(p.descripcion) > 80 else p.descripcion,
        "costo": int(p.costo),
        "imagen_url": p.imagen.url if p.imagen else ""
    } for p in similares]

    return JsonResponse({"recomendaciones": data})


# ================================
#  DESCARGAR BOLETA PDF
# ================================

def descargar_boleta(request, boleta_id):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from django.http import HttpResponse
    from .models import Boleta

    try:
        boleta = Boleta.objects.get(numero=boleta_id)
    except Boleta.DoesNotExist:
        return HttpResponse("Boleta no encontrada", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boleta_SII_{boleta.numero}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 50

    # --- ENCABEZADO ---
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, y, "BOLETA ELECTRÓNICA")

    y -= 22
    p.setFont("Helvetica", 11)
    p.drawString(50, y, "Representación impresa del documento electrónico")

    p.setFont("Helvetica-Bold", 14)
    p.drawString(400, height - 50, f"FOLIO N° {boleta.numero:06d}")

    y -= 20
    p.line(40, y, width - 40, y)

    # --- EMISOR ---
    y -= 25
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "EMISOR:")

    p.setFont("Helvetica", 11)
    y -= 18
    p.drawString(50, y, "MotoAutoDast")
    y -= 16 # Considerar obtener estos datos de settings.py o un modelo de configuración
    p.drawString(50, y, f"RUT: {getattr(settings, 'EMPRESA_RUT', '76.123.456-7')}")
    y -= 16
    p.drawString(50, y, f"Giro: {getattr(settings, 'EMPRESA_GIRO', 'Venta de repuestos automotrices')}")
    y -= 16
    p.drawString(50, y, f"Dirección: {getattr(settings, 'EMPRESA_DIRECCION', 'Pasaje Piedras Negras 9483')}")
    y -= 16
    p.drawString(50, y, f"Teléfono: {getattr(settings, 'EMPRESA_TELEFONO', '+56 9 8123 4032')}")

    y -= 20
    p.line(40, y, width - 40, y)

    # --- CLIENTE ---
    y -= 25
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "CLIENTE:")

    p.setFont("Helvetica", 11)
    y -= 18
    p.drawString(50, y, f"Nombre: {boleta.usuario.username}")
    y -= 16
  
  
    # --- DETALLE ---
    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "DETALLE DE PRODUCTOS")
    y -= 20

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Producto")
    p.drawString(250, y, "Cant.")
    p.drawString(320, y, "P.Unit")
    p.drawString(420, y, "Total")

    y -= 15
    p.line(40, y, width - 40, y)
    y -= 20

    p.setFont("Helvetica", 11)

    for item in boleta.detalle:
    # Conversión a números reales
        precio_unit = int(item["precio"])
        cantidad = int(item["cantidad"])
        total_item = precio_unit * cantidad

# Dibujar datos
        p.drawString(50, y, item["producto"])
        p.drawString(250, y, str(cantidad))
        p.drawString(320, y, f"${precio_unit:,}".replace(",", "."))
        p.drawString(420, y, f"${total_item:,}".replace(",", "."))

        y -= 22


    # --- TOTALES (con IVA 19%) ---
    neto = int(boleta.monto_total / 1.19)
    iva = boleta.monto_total - neto

    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, y, f"TOTAL NETO: ${neto}")
    y -= 20
    p.drawString(350, y, f"IVA (19%): ${iva}")
    y -= 20
    p.drawString(350, y, f"TOTAL A PAGAR: ${boleta.monto_total}")

    # --- FOOTER ---
    y -= 50
    p.setFillColor(colors.grey)
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, y, "Gracias por su compra.")
    y -= 15
    p.drawString(50, y, "Representación impresa del documento electrónico — No es un documento tributario real")

    p.save()
    return response

def pedido_detalle(request, pedido_id):
    pedido = Compra.objects.get(id=pedido_id)
    productos = ProductoCompra.objects.filter(compra=pedido)
    boleta = Boleta.objects.filter(usuario=request.user, monto_total=pedido.monto).last()

    return render(request, "pedido_detalle.html", {
        "pedido": pedido,
        "productos": productos,
        "boleta": boleta
    })