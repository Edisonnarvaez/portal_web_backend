from django.contrib import admin
from .models.company import Company
from .models.department import Department
from .models.headquarters import Headquarters
from .models.process_type import ProcessType
from .models.process import Process

# Configurar el modelo Company en el admin
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'nit', 'status')
    search_fields = ('name', 'nit')
    list_filter = ('status',)
    ordering = ('id',)

# Configurar el modelo Department en el admin
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'status')
    search_fields = ('name', 'companyId__name')
    list_filter = ('status',)
    ordering = ('id',)

# Configurar el modelo Headquarters en el admin
@admin.register(Headquarters)
class HeadquartersAdmin(admin.ModelAdmin):
    list_display = ('id', 'habilitationCode', 'name', 'company', 'departament', 'city', 'address', 'habilitationDate', 'closingDate', 'status')
    search_fields = ('habilitationCode', 'name', 'company__name')
    list_filter = ('status',)
    ordering = ('id',)

@admin.register(ProcessType)
class ProcessTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'company', 'creationDate', 'updateDate')
    search_fields = ('name', 'code', 'companyId__name')
    list_filter = ('status', 'creationDate', 'updateDate')
    ordering = ('creationDate',)

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'processType', 'department', 'version', 'status', 'creationDate', 'updateDate')
    search_fields = ('name', 'code', 'processType_name', 'department_name')
    list_filter = ('status', 'creationDate', 'updateDate')
    ordering = ('creationDate',)
