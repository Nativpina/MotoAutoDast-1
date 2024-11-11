from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Producto, Categoria
# Create your views here.

@login_required
def inicio(req):
    return render(req, 'inicio.html')

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'catalogoTest.html', {'productos': productos})

from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria
from django.contrib.auth.decorators import login_required

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

def olvidopass(request):
    return render(request, 'registration/olvidopass.html')