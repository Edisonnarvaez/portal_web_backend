from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, App

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_roles', 'is_staff', 'is_active')
    list_filter = ('roles', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('roles',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Roles', {'fields': ('roles',)}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'roles', 'is_staff', 'is_active')}
        ),
    )

    def get_roles(self, obj):
        return ", ".join([f"{role.name} ({role.app.name})" for role in obj.roles.all()])
    get_roles.short_description = 'Roles'

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'app')
    search_fields = ('name', 'app__name')
    list_filter = ('app',)

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
