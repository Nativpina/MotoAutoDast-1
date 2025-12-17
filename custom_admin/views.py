from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from MainApp.models import Compra, Cliente, Producto, Categoria, Bodega, ProductoCompra, Visita
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta

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

    # ------------------- INGRESOS DIARIOS (ÚLTIMOS 30 DÍAS) -------------------
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=29)  # Cambiado a 29 para incluir hoy
    
    # Obtener ventas por día
    ventas_por_dia = []
    dias_labels = []
    
    for i in range(30):
        dia = hace_30_dias + timedelta(days=i)
        total_dia = Compra.objects.filter(
            fecha_compra=dia,
            estado='enviado'
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        ventas_por_dia.append(float(total_dia))
        dias_labels.append(dia.strftime('%d/%m'))

    # ------------------- VENTAS POR CATEGORÍA (TOP 5 en CLP) -------------------
    ventas_categoria = ProductoCompra.objects.filter(
        compra__estado='enviado'
    ).values(
        'producto__categoria__nombre_categoria'
    ).annotate(
        total_ventas=Sum(F('cantidad') * F('precio_unitario_venta'))
    ).order_by('-total_ventas')[:5]
    
    categorias_labels = [v['producto__categoria__nombre_categoria'] for v in ventas_categoria]
    categorias_valores = [float(v['total_ventas']) for v in ventas_categoria]

    # ------------------- CONTEXTO -------------------

    context = {
        "total_pedidos_pendientes": total_pedidos_pendientes,
        "total_pedidos_enviados": total_pedidos_enviados,
        "total_ventas": total_ventas,
        "dias_labels": dias_labels,
        "ventas_por_dia": ventas_por_dia,
        "categorias_labels": categorias_labels,
        "categorias_valores": categorias_valores,
    }

    return render(req, "admin/dashboard.html", context)

@login_required
def pagos_view(request):
    if not request.user.is_superuser:
        return redirect('/')
    
    pagos = Compra.objects.select_related('cliente').order_by('-fecha_compra')
    
    return render(request, 'admin/pagos.html', {'pagos': pagos})


@login_required
def venta_manual_view(request):
    if not request.user.is_superuser:
        return redirect('/')
    
    # Obtener filtros
    categoria_id = request.GET.get('categoria')
    bodega_id = request.GET.get('bodega')
    busqueda = request.GET.get('q', '').strip()
    
    # Filtrar productos
    productos = Producto.objects.filter(stock__gt=0)
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if bodega_id:
        productos = productos.filter(bodega_id=bodega_id)
    
    if busqueda:
        productos = productos.filter(nombre_producto__icontains=busqueda)
    
    productos = productos.select_related('categoria', 'bodega').order_by('nombre_producto')
    
    # Manejar POST - registrar venta
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = request.POST.get('cantidad')
        cliente_nombre = request.POST.get('cliente_nombre', '').strip()
        fecha_venta = request.POST.get('fecha_venta')
        monto_personalizado = request.POST.get('monto_personalizado')
        usar_monto_custom = request.POST.get('usar_monto_custom') == 'on'
        
        # Validaciones
        try:
            if not all([producto_id, cantidad, cliente_nombre, fecha_venta]):
                raise ValueError('Todos los campos son obligatorios.')
            
            producto = Producto.objects.get(id=producto_id)
            cantidad = int(cantidad)
            
            if cantidad <= 0:
                raise ValueError('La cantidad debe ser mayor a 0.')
            
            if cantidad > producto.stock:
                raise ValueError(f'Stock insuficiente. Solo hay {producto.stock} unidades disponibles.')
            
            # Calcular monto
            if usar_monto_custom:
                monto_total = float(monto_personalizado)
                precio_unitario = monto_total / cantidad
            else:
                precio_unitario = producto.costo
                monto_total = cantidad * precio_unitario
            
            # Crear o buscar cliente
            cliente, created = Cliente.objects.get_or_create(
                nombre_cliente=cliente_nombre,
                defaults={'email': 'venta_manual@local.com', 'num': 0}
            )
            
            # Crear la compra
            compra = Compra.objects.create(
                fecha_compra=fecha_venta,
                cliente=cliente,
                estado='enviado',
                monto=monto_total,
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
            
        except ValueError as ve:
            messages.error(request, str(ve))
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado.')
        except Exception as e:
            messages.error(request, f'Error al registrar la venta: {str(e)}')
    
    # Datos para filtros
    categorias = Categoria.objects.all()
    bodegas = Bodega.objects.all()
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'bodegas': bodegas,
        'categoria_seleccionada': categoria_id,
        'bodega_seleccionada': bodega_id,
        'busqueda': busqueda,
    }
    
    return render(request, 'admin/venta_manual.html', context)


def ajustes(request):
    return render(request, 'admin/ajustes.html')
