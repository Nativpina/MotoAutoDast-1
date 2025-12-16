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
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error en admin_login: {str(e)}", exc_info=True)
        messages.error(req, 'Error en el inicio de sesión. Intente nuevamente.')
        return redirect('/')




@login_required(login_url='/admin/')
def dashboard(req):

    # Solo superusuarios pueden entrar
    if not req.user.is_superuser:
        messages.warning(req, 'No tienes permisos para acceder al panel de administración.')
        return redirect('/')

    # ------------------- TARJETAS SUPERIORES -------------------
    try:
        total_pedidos_pendientes = Compra.objects.filter(estado='pendiente').count()
    except Exception:
        total_pedidos_pendientes = 0

    try:
        total_pedidos_enviados = Compra.objects.filter(estado='enviado').count()
    except Exception:
        total_pedidos_enviados = 0

    try:
        total_ventas = Compra.objects.filter(
            estado='enviado'
        ).aggregate(total=Sum('monto'))['total'] or 0
    except Exception:
        total_ventas = 0

    # ------------------- VISITAS POR MES -------------------
    meses_labels = [
        "Enero","Febrero","Marzo","Abril","Mayo","Junio",
        "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
    ]

    visitas_data = []
    try:
        visitas_data = [
            Visita.objects.filter(fecha__month=i).count() for i in range(1, 13)
        ]
    except Exception:
        visitas_data = [0] * 12

    # ------------------- CATEGORÍAS MÁS VISTAS -------------------
    categorias_labels = []
    categorias_valores = []

    try:
        for categoria in Categoria.objects.all():
            try:
                visitas_categoria = Visita.objects.filter(
                    producto__categoria=categoria
                ).count()
                categorias_labels.append(str(categoria.nombre_categoria))
                categorias_valores.append(int(visitas_categoria))
            except Exception:
                continue
    except Exception:
        pass

    # Si no hay categorías, agregar valores por defecto para el gráfico
    if not categorias_labels:
        categorias_labels = ["Sin datos"]
        categorias_valores = [0]

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

@login_required(login_url='/admin/')
def pagos_view(request):
    if not request.user.is_superuser:
        messages.warning(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('/')
    pagos = Compra.objects.select_related('cliente').order_by('-fecha_compra')
    return render(request, 'admin/pagos.html', {'pagos': pagos})


def ajustes(request):
    return render(request, 'admin/ajustes.html')
