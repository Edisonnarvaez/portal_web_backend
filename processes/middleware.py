# processes/middleware.py
class CustomXFrameOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Permitir framing para endpoints de preview
        if (request.path.startswith('/api/processes/documentos/') and 
            '/preview/' in request.path):
            response['X-Frame-Options'] = 'SAMEORIGIN'
        elif request.path.startswith('/media/'):
            response['X-Frame-Options'] = 'SAMEORIGIN'
        else:
            response['X-Frame-Options'] = 'DENY'
        
        return response

# Añade a MIDDLEWARE en settings.py
#MIDDLEWARE = [
#    # ... otro middleware
#    'processes.middleware.CustomXFrameOptionsMiddleware',
#]