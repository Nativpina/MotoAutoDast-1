from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from MainApp.forms import ProductoForm, ContactoForm
from .models import Producto, Categoria, Categoria, Bodega, Producto, Contacto
from .forms import CustomUserCreationForm  # Importa el formulario personalizado
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator







def inicio(request):
    productos = Producto.objects.all()  
    return render(request, 'inicio.html', {'productos': productos})

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

def Aceites(req):
    try:
        categoria = Categoria.objects.get(nombre_categoria="Aceite")
        productos = Producto.objects.filter(categoria=categoria)
    except Categoria.DoesNotExist:
        productos = []
    return render(req, 'catalogo.html', {'productos': productos, 'categoria': 'Aceite'})

def Accesorios(req):
    try:
        categoria = Categoria.objects.get(nombre_categoria="Accesorios")
        productos = Producto.objects.filter(categoria=categoria)
    except Categoria.DoesNotExist:
        productos = []
    return render(req, 'catalogo.html', {'productos': productos, 'categoria': 'Accesorios'})

def Neumaticos(req):
    try:
        categoria = Categoria.objects.get(nombre_categoria="Neumaticos")
        productos = Producto.objects.filter(categoria=categoria)
    except Categoria.DoesNotExist:
        productos = []
    return render(req, 'catalogo.html', {'productos': productos, 'categoria': 'Neumáticos'})

def Repuestos(req):
    try:
        categoria = Categoria.objects.get(nombre_categoria="Repuestos")
        productos = Producto.objects.filter(categoria=categoria)
    except Categoria.DoesNotExist:
        productos = []
    return render(req, 'catalogo.html', {'productos': productos, 'categoria': 'Repuestos'})

def producto_detalle(req, id):
    producto = get_object_or_404(Producto, id=id)
    return render(req, 'producto_detalle.html', {'producto': producto})

def restablecer_contrasena(request):
    return render(request, 'registration/restablecer_contrasena.html', {'mostrar_busqueda': False})





def buscar_productos(request):
    query = request.GET.get('q')  # Captura el término de búsqueda desde el input "q"
    productos = Producto.objects.filter(nombre_producto__icontains=query) if query else []
    categoria = f"Resultados para '{query}'" if query else "Sin resultados"
    return render(request, 'busqueda.html', {'productos': productos, 'categoria': categoria})

def buscar_productos(request):
    query = request.GET.get('q')  # Captura el término de búsqueda desde el input
    productos = Producto.objects.filter(nombre_producto__icontains=query) if query else []
    categoria = f"Resultados para '{query}'" if query else "Sin resultados"
    return render(request, 'busqueda.html', {'productos': productos, 'categoria': categoria})

def listar_productos(request):
    if not request.user.is_superuser:
        return redirect('/')
    productos = Producto.objects.all()  # Obtiene todos los productos
    return render(request, 'admin/productos.html', {'productos': productos})


def agregar_producto(request):
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')  # Redirige a la lista de productos después de guardar
    else:
        form = ProductoForm()

    # Obtiene las categorías y bodegas de la base de datos
    categorias = Categoria.objects.all()
    bodegas = Bodega.objects.all()

    return render(request, 'admin/agregar_producto.html', {
        'form': form,
        'categorias': categorias,
        'bodegas': bodegas,
    })

def editar_producto(request, producto_id):
    if not request.user.is_superuser:
        return redirect('/')    
    # Obtén el producto a editar
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')  # Redirige a la lista de productos
    else:
        form = ProductoForm(instance=producto)

    # Obtén todas las categorías y bodegas para los select
    categorias = Categoria.objects.all()
    bodegas = Bodega.objects.all()

    return render(request, 'admin/editar_producto.html', {
        'form': form,
        'producto': producto,
        'categorias': categorias,
        'bodegas': bodegas,
    })

def eliminar_producto(request, producto_id):
    if not request.user.is_superuser:
        return redirect('/')  
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        producto.delete()
        return redirect('listar_productos')  # Redirige a la lista de productos después de eliminar

    return render(request, 'admin/confirmar_eliminacion.html', {'producto': producto})


def form_contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_contactos')  # Redirige a la página donde se muestran los contactos
    else:
        form = ContactoForm()
    
    return render(request, 'contacto.html', {'form': form, 'mostrar_busqueda': False})

def lista_contactos(request):
    if not request.user.is_superuser:
        return redirect('/')  
    contactos = Contacto.objects.all().order_by('-fecha_envio')
    return render(request, 'admin/listaContacto.html', {'contactos': contactos})

def ajustes(request):
    if not request.user.is_superuser:
        return redirect('/')  
    return render(request, 'admin/ajustes.html')

def ayudaLogin(request):
    return render(request, 'admin/AyudaLogin.html')


def enviar_email_con_nombre_usuario(request, user_email):
    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        return  # Opcionalmente manejar el caso de usuario no encontrado
    
    # Preparar el contexto con el nombre de usuario
    current_site = get_current_site(request)
    context = {
        'username': user.username,  # Nombre de usuario
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    }

    # Renderizar el mensaje HTML y enviar el correo
    subject = "Restablece tu contraseña"
    message = render_to_string('emails/password_reset_email.html', context)
    email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
    email.attach_alternative(message, "text/html")
    email.send()