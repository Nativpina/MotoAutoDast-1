from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from MainApp.models import Producto, Compra, Cliente
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect

def admin_login(req):
    try:
        # Si el usuario ya está autenticado, redirige directamente al dashboard
        if req.user.is_authenticated:
            return redirect('/admin/dashboard/')
        
        if req.method == 'POST':
            # Obtener los datos del formulario
            username = req.POST.get('username')
            password = req.POST.get('password')

            # Verificar si el usuario existe 
            user_obj = User.objects.filter(username=username)
            if not user_obj.exists():
                messages.info(req, 'Cuenta no encontrada')
                return HttpResponseRedirect(req.META.get('HTTP_REFERER'))
            
            # Autenticar al usuario
            user_obj = authenticate(username=username, password=password)
            
            if user_obj and user_obj.is_superuser:
                # Iniciar sesión si el usuario es superusuario
                login(req, user_obj)
                # Redirige al dashboard del administrador
                return redirect('/admin/dashboard/')
            
            # Si las credenciales no son válidas
            messages.info(req, 'Contraseña Incorrecta')
            return redirect('/')
        
        # Renderizar la página de login si no es una solicitud POST
        return render(req, 'Adminlogin.html')
    
    except Exception as e:
        print(e)


@login_required
def dashboard(req):
    return render(req, 'dashboard.html')
    # Ejemplo de datos para el dashboard
    #total_pedidos_pendientes = Compra.objects.filter(estado='pendiente').count()
    #total_pedidos_enviados = Compra.objects.filter(estado='enviado').count()
    #total_ventas = Compra.objects.filter(estado='enviado').aggregate(total=sum('monto'))['total'] or 0
    #total_contactos = Cliente.objects.count()

    #context = {
        #'total_pedidos_pendientes': total_pedidos_pendientes,
        #'total_pedidos_enviados': total_pedidos_enviados,
        #'total_ventas': total_ventas,
        #'total_contactos': total_contactos,
    #}
    #return render(request, 'admin_dashboard.html', context)