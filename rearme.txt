## Pasos para ejecutar el proyecto - Python 3.12.10

# creación de entorno virtual
python -m venv venv

# activacion de entorno virtual
.\venv\Scripts\activate

# instalar archivo requirements
pip install -r requirements.txt

# realizar migraciones
python manage.py makemigrations
python manage.py migrate

# crear super usuario
python manage.py createsuperuser

# correr proyecto 
python manage.py runserver

## comandos git
# para hacer commit
git add .
git commit -m "Comentario"
git push

# ver estado 
git status

# cambiar de rama
git checkout nombreRama

# clonar el proyecto 
git clone https://github.com/RedMedicronIPS/backend_gestion_proveedores.git
     

## en caso de qie se incluyan nuevas librerias al proyecto 
# crear/actualizar archivo requirements 
pip freeze > requirements.txt

# instalar archivo requirements
pip install -r requirements.txt

# en produccion se puede utilizar 
python manage.py runserver 0.0.0.0:8081
# o 
python run_waitress.py