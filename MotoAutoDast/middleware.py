from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404
import os


class ServeMediaMiddleware:
    """
    Middleware para servir archivos media en producción usando WhiteNoise
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.media_storage = FileSystemStorage(location=settings.MEDIA_ROOT)

    def __call__(self, request):
        # Solo servir media en producción cuando DEBUG=False
        if not settings.DEBUG and request.path.startswith(settings.MEDIA_URL):
            # Obtener la ruta del archivo
            relative_path = request.path[len(settings.MEDIA_URL):]
            file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            
            # Verificar si el archivo existe
            if os.path.isfile(file_path):
                try:
                    # Servir el archivo
                    response = FileResponse(open(file_path, 'rb'))
                    # Agregar headers de cache
                    response['Cache-Control'] = 'public, max-age=31536000'
                    return response
                except Exception:
                    pass
            
            raise Http404("Media file not found")
        
        return self.get_response(request)
