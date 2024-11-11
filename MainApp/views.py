from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Producto, Categoria
from .forms import CustomUserCreationForm  # Importa el formulario personalizado

@login_required
def inicio(req):
    return render(req, 'inicio.html')

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'catalogoTest.html', {'productos': productos})

def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Usa el formulario personalizado
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Hubo un problema al registrarse. Por favor, verifica los datos e intenta nuevamente.')
    else:
        form = CustomUserCreationForm()  # Usa el formulario personalizado
    return render(request, 'registration/registro.html', {'form': form})

@login_required
def Aceites(req):
    try:
        categoria = Categoria.objects.get(nombre_categoria="Aceite")
        productos = Producto.objects.filter(categoria=categoria)
    except Categoria.DoesNotExist:
        productos = []
    return render(req, 'catalogo.html', {'productos': productos, 'categoria': 'Aceite'})

@login_required
def Accesorios(req):
    try:
        categoria = Categoria.objects.get(nombre_categoria="Accesorios")
        productos = Producto.objects.filter(categoria=categoria)
    except Categoria.DoesNotExist:
        productos = []
    return render(req, 'catalogo.html', {'productos': productos, 'categoria': 'Accesorios'})

@login_required
def Neumaticos(req):
    try:
        categoria = Categoria.objects.get(nombre_categoria="Neumaticos")
        productos = Producto.objects.filter(categoria=categoria)
    except Categoria.DoesNotExist:
        productos = []
    return render(req, 'catalogo.html', {'productos': productos, 'categoria': 'Neumáticos'})

@login_required
def Repuestos(req):
    try:
        categoria = Categoria.objects.get(nombre_categoria="Repuestos")
        productos = Producto.objects.filter(categoria=categoria)
    except Categoria.DoesNotExist:
        productos = []
    return render(req, 'catalogo.html', {'productos': productos, 'categoria': 'Repuestos'})

@login_required
def producto_detalle(req, id):
    producto = get_object_or_404(Producto, id=id)
    return render(req, 'producto_detalle.html', {'producto': producto})

def restablecer_contrasena(request):
    return render(request, 'registration/restablecer_contrasena.html')

def contacto(request):
    return render(request, 'contacto.html', {'mostrar_busqueda': False})
