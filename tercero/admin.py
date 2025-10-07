from django.contrib import admin
from .models import Terceros
from .models import Pais
from .models import Departamento
from .models import Municipio
from .models import TipoTercero
from django.forms.widgets import RadioSelect


@admin.register(Terceros)
class TercerosAdmin(admin.ModelAdmin):
    list_display = ('tercero_nombre_completo', 'tercero_email', 'tercero_tipo')
    search_fields = ('tercero_nombre_completo', 'tercero_email')
  
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "tercero_tipo":
            kwargs["widget"] = RadioSelect()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('pais_id', 'pais_nombre')
    search_fields = ('id', 'pais_id', 'pais_nombre')


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('departamento_id', 'departamento_nombre', 'departamento_pais')
    search_fields = ('id', 'departamento_id', 'departamento_nombre', 'departamento_pais')


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('municipio_id', 'municipio_nombre', 'municipio_departamento')
    search_fields = ( 'id','municipio_id', 'municipio_nombre', 'municipio_departamento')

    
@admin.register(TipoTercero)
class TipoTerceroAdmin(admin.ModelAdmin):
    list_display = ('tercero_id', 'nombre')
    search_fields = ('nombre',)

