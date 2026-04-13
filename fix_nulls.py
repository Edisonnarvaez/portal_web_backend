#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from soportes.models import SoporteDocumental

# Eliminar registros con empresa_id NULL
deleted, _ = SoporteDocumental.objects.filter(empresa__isnull=True).delete()
print(f'Registros eliminados: {deleted}')

# Verificar
print('Total registros después:', SoporteDocumental.objects.count())
print('Con empresa NULL ahora:', SoporteDocumental.objects.filter(empresa__isnull=True).count())
