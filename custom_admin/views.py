from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from MainApp.models import Compra, Cliente, Producto, Categoria, Bodega, ProductoCompra, Visita, EntregaDomicilio, HistorialCambios
from django.db.models import Sum, Count, F, Q
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

    # Pedidos Enviados/Entregados
    total_pedidos_enviados = Compra.objects.filter(estado__in=['enviado', 'entregado']).count()

    # Ventas Totales (todas las compras excepto canceladas)
    total_ventas = Compra.objects.exclude(
        estado='cancelado'
    ).aggregate(
        total=Sum('monto')
    )['total'] or 0

    # ------------------- INGRESOS DIARIOS (ÚLTIMOS 30 DÍAS) -------------------
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=29)  # Cambiado a 29 para incluir hoy
    
    # Obtener ventas por día (incluyendo todas las compras de usuarios)
    ventas_por_dia = []
    dias_labels = []
    
    for i in range(30):
        dia = hace_30_dias + timedelta(days=i)
        # Incluir compras completadas, no solo 'enviado'
        total_dia = Compra.objects.filter(
            fecha_compra=dia
        ).exclude(estado='cancelado').aggregate(total=Sum('monto'))['total'] or 0
        
        ventas_por_dia.append(float(total_dia))
        dias_labels.append(dia.strftime('%d/%m'))

    # ------------------- VENTAS POR CATEGORÍA (TOP 5 en CLP) -------------------
    ventas_categoria = ProductoCompra.objects.filter(
        compra__estado__in=['pendiente', 'en_camino', 'entregado', 'enviado']
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
    """Vista de ventas/pagos con filtros integrados"""
    if not request.user.is_superuser:
        return redirect('/')
    
    compras = Compra.objects.all().select_related('cliente').order_by('-fecha_compra')
    
    # Filtros
    estado = request.GET.get('estado', '')
    tipo_entrega = request.GET.get('tipo_entrega', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    busqueda_cliente = request.GET.get('cliente', '')
    
    if estado:
        compras = compras.filter(estado=estado)
    
    if tipo_entrega:
        compras = compras.filter(tipo_entrega=tipo_entrega)
    
    if fecha_desde:
        compras = compras.filter(fecha_compra__gte=fecha_desde)
    
    if fecha_hasta:
        compras = compras.filter(fecha_compra__lte=fecha_hasta)
    
    if busqueda_cliente:
        compras = compras.filter(
            Q(cliente__nombre_cliente__icontains=busqueda_cliente) | 
            Q(cliente__email__icontains=busqueda_cliente)
        )
    
    context = {
        'pagos': compras,
        'compras': compras,
        'filtro_estado': estado,
        'filtro_tipo_entrega': tipo_entrega,
        'filtro_fecha_desde': fecha_desde,
        'filtro_fecha_hasta': fecha_hasta,
        'filtro_cliente': busqueda_cliente,
    }
    
    return render(request, 'admin/pagos.html', context)


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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from MainApp.models import Compra, ProductoCompra, HistorialAdmin


@login_required
def pagos_detalle_view(request):
    """Vista mejorada de pagos con filtros"""
    if not request.user.is_superuser:
        return redirect('/')
    
    compras = Compra.objects.all().select_related('cliente').order_by('-fecha_compra')
    
    # Filtros
    estado = request.GET.get('estado', '')
    tipo_entrega = request.GET.get('tipo_entrega', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    busqueda_cliente = request.GET.get('cliente', '')
    
    if estado:
        compras = compras.filter(estado=estado)
    
    if tipo_entrega:
        compras = compras.filter(tipo_entrega=tipo_entrega)
    
    if fecha_desde:
        compras = compras.filter(fecha_compra__gte=fecha_desde)
    
    if fecha_hasta:
        compras = compras.filter(fecha_compra__lte=fecha_hasta)
    
    if busqueda_cliente:
        compras = compras.filter(
            Q(cliente__nombre_cliente__icontains=busqueda_cliente) | 
            Q(cliente__email__icontains=busqueda_cliente)
        )
    
    context = {
        'compras': compras,
        'filtro_estado': estado,
        'filtro_tipo_entrega': tipo_entrega,
        'filtro_fecha_desde': fecha_desde,
        'filtro_fecha_hasta': fecha_hasta,
        'filtro_cliente': busqueda_cliente,
    }
    
    return render(request, 'admin/pagos_detalle.html', context)


@login_required
def entregas_pendientes_view(request):
    """Vista para gestión de entregas a domicilio"""
    if not request.user.is_superuser:
        return redirect('/')
    
    # Separar entregas por estado
    entregas_pendientes = Compra.objects.filter(
        tipo_entrega='envio',
        estado='pendiente'
    ).select_related('cliente').order_by('fecha_compra')
    
    entregas_en_camino = Compra.objects.filter(
        tipo_entrega='envio',
        estado='en_camino'
    ).select_related('cliente').order_by('fecha_compra')
    
    entregas_no_entregadas = Compra.objects.filter(
        tipo_entrega='envio',
        estado='no_entregado'
    ).select_related('cliente').order_by('fecha_compra')
    
    context = {
        'entregas_pendientes': entregas_pendientes,
        'entregas_en_camino': entregas_en_camino,
        'entregas_no_entregadas': entregas_no_entregadas,
        'pendientes_count': entregas_pendientes.count(),
        'en_camino_count': entregas_en_camino.count(),
        'no_entregados_count': entregas_no_entregadas.count(),
    }
    
    return render(request, 'admin/entregas_pendientes.html', context)


@login_required
def iniciar_entrega(request, entrega_id):
    """Marca el inicio del recorrido de entrega"""
    if not request.user.is_superuser:
        return redirect('admin:entregas_pendientes')
    
    compra = get_object_or_404(Compra, id=entrega_id)
    
    if not compra.delivery_iniciado:
        compra.delivery_iniciado = timezone.now()
        compra.estado = 'en_camino'
        compra.save()
        
        # Registrar en historial
        HistorialCambios.objects.create(
            usuario=request.user,
            accion='Inicio de entrega',
            detalle=f'Pedido #{compra.id} - Cliente: {compra.cliente.nombre_cliente}',
            tipo='entrega'
        )
        
        messages.success(request, f'Entrega iniciada para pedido #{compra.id}')
    else:
        messages.info(request, 'Esta entrega ya fue iniciada.')
    
    return redirect('admin:entregas_pendientes')


@login_required
def finalizar_entrega(request, entrega_id):
    """Finaliza la entrega y registra el resultado"""
    if not request.user.is_superuser:
        return redirect('/')
    
    compra = get_object_or_404(Compra, id=entrega_id)
    
    if request.method == 'POST':
        fue_entregado = request.POST.get('entregado') == 'si'
        
        compra.delivery_finalizado = timezone.now()
        compra.intentos_entrega += 1
        
        if fue_entregado:
            compra.estado = 'entregado'
            
            # Registrar en historial
            HistorialCambios.objects.create(
                usuario=request.user,
                accion='Entrega completada',
                detalle=f'Pedido #{compra.id} entregado exitosamente',
                tipo='entrega'
            )
            
            messages.success(request, f'Entrega completada para pedido #{compra.id}')
        else:
            motivo = request.POST.get('motivo_no_entrega', '')
            reintentar = request.POST.get('reintentar') == 'si'
            
            compra.motivo_no_entrega = motivo
            
            if reintentar:
                compra.estado = 'no_entregado'
                compra.delivery_iniciado = None  # Resetear para permitir nuevo intento
            else:
                compra.estado = 'cancelado'
            
            # Registrar en historial
            HistorialCambios.objects.create(
                usuario=request.user,
                accion='Entrega fallida',
                detalle=f'Pedido #{compra.id} no entregado. Motivo: {motivo}. Reintentar: {"Sí" if reintentar else "No"}',
                tipo='entrega'
            )
            
            messages.warning(request, f'Pedido #{compra.id} marcado como no entregado')
        
        compra.save()
    
    return redirect('admin:entregas_pendientes')


@login_required
def historial_cambios_view(request):
    """Vista para el historial de cambios administrativos"""
    if not request.user.is_superuser:
        return redirect('/')
    
    cambios = HistorialCambios.objects.all().select_related('usuario')
    
    # Filtros
    tipo = request.GET.get('tipo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    usuario_filtro = request.GET.get('usuario', '')
    
    if tipo:
        cambios = cambios.filter(tipo=tipo)
    
    if fecha_desde:
        cambios = cambios.filter(fecha__gte=fecha_desde)
    
    if fecha_hasta:
        cambios = cambios.filter(fecha__lte=fecha_hasta)
    
    if usuario_filtro:
        cambios = cambios.filter(usuario__username__icontains=usuario_filtro)
    
    context = {
        'cambios': cambios[:100],  # Limitar a 100 registros mÃ¡s recientes
        'filtro_tipo': tipo,
        'filtro_fecha_desde': fecha_desde,
        'filtro_fecha_hasta': fecha_hasta,
        'filtro_usuario': usuario_filtro,
    }
    
    return render(request, 'admin/historial_cambios.html', context)
