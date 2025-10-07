from waitress import serve
from backend.wsgi import application  

serve(application, host="127.0.0.1", port=8081)



