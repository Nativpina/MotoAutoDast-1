from MainApp.models import Categoria

def categorias_navbar(request):
    """Context processor para mostrar categorías en el navbar"""
    categorias = Categoria.objects.all().order_by('nombre_categoria')
    return {'categorias_navbar': categorias}
