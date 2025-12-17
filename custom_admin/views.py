from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from MainApp.models import Compra, Cliente
from django.db.models import Sum
from MainApp.models import Compra, Producto, Categoria
from django.db.models import Sum, Count
from django.utils import timezone
from MainApp.models import Visita

def admin_login(req):
    try:
        if req.user.is_authenticated:
            if req.user.is_superuser:
                return redirect('/admin/dashboard/')
            else:
                return redirect('/')  # Redirige a la página de inicio si no es superusuario

        if req.method == 'POST':
            username = req.POST.get('username')
            password = req.POST.get('password')

            # Verificar si el usuario existe
            user_obj = User.objects.filter(username=username).first()
            if not user_obj:
                messages.info(req, 'Cuenta no encontrada')
                return HttpResponseRedirect(req.META.get('HTTP_REFERER'))
            
            # Autenticar al usuario
            user_obj = authenticate(username=username, password=password)

            if user_obj:
                if user_obj.is_superuser:
                    # Iniciar sesión y redirigir al dashboard si es superusuario
                    login(req, user_obj)
                    return redirect('/admin/dashboard/')
                else:
                    # Redirige a la página de inicio si el usuario no es superusuario
                    messages.info(req, 'No tienes permiso para acceder a esta sección')
                    return redirect('/')
            else:
                messages.info(req, 'Contraseña Incorrecta')
                return HttpResponseRedirect(req.META.get('HTTP_REFERER'))

        return render(req, 'admin/Adminlogin.html')
    
    except Exception as e:
        print(e)




@login_required
def dashboard(req):

    # Solo superusuarios pueden entrar
    if not req.user.is_superuser:
        return redirect('/')

    # ------------------- TARJETAS SUPERIORES -------------------

    # Pedidos Pendientes
    total_pedidos_pendientes = Compra.objects.filter(estado='pendiente').count()

    # Pedidos Enviados
    total_pedidos_enviados = Compra.objects.filter(estado='enviado').count()

    # Ventas Totales
    total_ventas = Compra.objects.filter(
        estado='enviado'
    ).aggregate(
        total=Sum('monto')
    )['total'] or 0

    # ------------------- VISITAS POR MES -------------------

    meses_labels = [
        "Enero","Febrero","Marzo","Abril","Mayo","Junio",
        "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
    ]

    visitas_data = [
        Visita.objects.filter(fecha__month=i).count() for i in range(1, 13)
    ]

    # ------------------- CATEGORÍAS MÁS VISTAS -------------------

    categorias_labels = []
    categorias_valores = []

    for categoria in Categoria.objects.all():
        visitas_categoria = Visita.objects.filter(
            producto__categoria=categoria
        ).count()

        categorias_labels.append(str(categoria.nombre_categoria))
        categorias_valores.append(int(visitas_categoria))

    # ------------------- CONTEXTO -------------------

    context = {
        "total_pedidos_pendientes": total_pedidos_pendientes,
        "total_pedidos_enviados": total_pedidos_enviados,
        "total_ventas": total_ventas,
        "meses_labels": meses_labels,
        "visitas_data": visitas_data,
        "categorias_labels": categorias_labels,
        "categorias_valores": categorias_valores,
    }

    return render(req, "admin/dashboard.html", context)

@login_required
def pagos_view(request):
    if not request.user.is_superuser:
        return redirect('/')
    
    # Manejar creación de venta manual
    if request.method == 'POST' and 'venta_manual' in request.POST:
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 0))
        precio_unitario = request.POST.get('precio_unitario')
        cliente_nombre = request.POST.get('cliente_nombre', '').strip()
        
        # Validaciones
        if not producto_id or cantidad <= 0 or not precio_unitario or not cliente_nombre:
            messages.error(request, 'Todos los campos son obligatorios y la cantidad debe ser mayor a 0.')
        else:
            try:
                producto = Producto.objects.get(id=producto_id)
                precio_unitario = float(precio_unitario)
                
                # Validar stock disponible
                if cantidad > producto.stock:
                    messages.error(request, f'Stock insuficiente. Solo hay {producto.stock} unidades disponibles.')
                else:
                    # Crear o buscar cliente genérico para ventas manuales
                    cliente, created = Cliente.objects.get_or_create(
                        nombre_cliente=cliente_nombre,
                        defaults={'email': 'venta_manual@local.com', 'num': 0}
                    )
                    
                    # Crear la compra
                    compra = Compra.objects.create(
                        fecha_compra=timezone.now().date(),
                        cliente=cliente,
                        estado='enviado',
                        monto=cantidad * precio_unitario,
                        tipo_entrega='retiro'
                    )
                    
                    # Crear el producto de compra
                    ProductoCompra.objects.create(
                        compra=compra,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario_venta=precio_unitario
                    )
                    
                    # Restar del stock
                    producto.stock -= cantidad
                    producto.save()
                    
                    messages.success(request, f'Venta manual registrada exitosamente. Stock actualizado: {producto.stock} unidades.')
                    return redirect('admin:pagos')
                    
            except Producto.DoesNotExist:
                messages.error(request, 'Producto no encontrado.')
            except ValueError:
                messages.error(request, 'Precio unitario inválido.')
            except Exception as e:
                messages.error(request, f'Error al registrar la venta: {str(e)}')
    
    pagos = Compra.objects.select_related('cliente').order_by('-fecha_compra')
    productos = Producto.objects.filter(stock__gt=0).order_by('nombre_producto')
    
    return render(request, 'admin/pagos.html', {
        'pagos': pagos,
        'productos': productos
    })


def ajustes(request):
    return render(request, 'admin/ajustes.html')
