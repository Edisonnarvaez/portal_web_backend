#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from soportes.models import SoporteDocumental

print('Total registros:', SoporteDocumental.objects.count())
print('Con empresa NULL:', SoporteDocumental.objects.filter(empresa__isnull=True).count())
print('Con prestador NULL:', SoporteDocumental.objects.filter(prestador__isnull=True).count())
