#!/usr/bin/env python
"""
Test script to validate Django Admin configuration.
Verifies that the AutoevaluacionAdmin form loads without FieldError.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.admin import AdminSite
from habilitacion.admin import AutoevaluacionAdmin
from habilitacion.models import Autoevaluacion, DatosPrestador
from companies.models import Company
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

# Create test data
try:
    company = Company.objects.create(
        name='Test Hospital',
        nit='123456789',
        foundationDate='2020-01-15'
    )
    
    datos_prestador = DatosPrestador.objects.create(
        company=company,
        codigo_reps='110001234567',
        clase_prestador='IPS',
        estado_habilitacion='EN_PROCESO',
    )
    
    autoevaluacion = Autoevaluacion.objects.create(
        datos_prestador=datos_prestador,
        periodo=2024,
        numero_autoevaluacion='AUT-110001234567-2024',
        version=1,
        fecha_vencimiento='2024-12-31',
    )
    
    # Test admin configuration
    admin_site = AdminSite()
    admin = AutoevaluacionAdmin(Autoevaluacion, admin_site)
    
    # Try to get the form - this is where the FieldError would occur
    form_class = admin.get_form(None, autoevaluacion)
    
    print("✓ Admin form loaded successfully!")
    print(f"✓ Form fields: {list(form_class.base_fields.keys())}")
    print(f"✓ Readonly fields configured: {admin.readonly_fields}")
    print("\n✅ VALIDACIÓN EXITOSA: No hay errores de FieldError en el admin")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    # Cleanup
    try:
        autoevaluacion.delete()
        datos_prestador.delete()
        company.delete()
    except:
        pass
