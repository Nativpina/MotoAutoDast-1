from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

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
    # Redirige a la página de inicio si el usuario no es superusuario
    if not req.user.is_superuser:
        return redirect('/')
    return render(req, 'admin/dashboard.html')

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