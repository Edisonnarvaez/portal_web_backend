from django.contrib import admin
from .models.company import Company
from .models.department import Department
from .models.headquarters import Headquarters
from .models.parameters import Region, Municipality
from .models.process_type import ProcessType
from .models.process import Process

# Configurar el modelo Company en el admin
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number_document', 'status')
    search_fields = ('name', 'number_document')
    list_filter = ('status',)
    ordering = ('id',)

# Configurar el modelo Department en el admin
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'status')
    search_fields = ('name', 'company__name')
    list_filter = ('status',)
    ordering = ('id',)

# Configurar el modelo Headquarters en el admin
@admin.register(Headquarters)
class HeadquartersAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        #'habilitationCode',
        'name',
        'company',
        'region',
        'municipality',
        'address',
        'creationDate',
        'updateDate',
        'status',
    )
    search_fields = ('name', 'company__name')
    list_filter = ('status',)
    ordering = ('id',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name')
    search_fields = ('code', 'name')
    ordering = ('id',)


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'region')
    search_fields = ('code', 'name', 'region__name', 'region__code')
    list_filter = ('region',)
    ordering = ('id',)

@admin.register(ProcessType)
class ProcessTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'company', 'creationDate', 'updateDate')
    search_fields = ('name', 'description', 'company__name')
    list_filter = ('status', 'creationDate', 'updateDate')
    ordering = ('creationDate',)

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'processType', 'department', 'version', 'status', 'creationDate', 'updateDate')
    search_fields = ('name', 'code', 'processType__name', 'department__name')
    list_filter = ('status', 'creationDate', 'updateDate')
    ordering = ('creationDate',)
