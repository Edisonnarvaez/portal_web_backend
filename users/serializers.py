from rest_framework import serializers
from .models import User, Role, App
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ['id', 'name']

class RoleSerializer(serializers.ModelSerializer):
    #app = serializers.StringRelatedField()
    app = AppSerializer(read_only=True)
    class Meta:
        model = Role
        fields = ['id', 'name', 'app']

class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'roles',
            'is_2fa_enabled', 'profile_picture', 'date_joined'
        ]

    def to_representation(self, instance):
        """Devuelve la URL absoluta o None o un ícono por defecto si no hay foto."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        if instance.profile_picture:
            url = instance.profile_picture.url
            if request is not None:
                data['profile_picture'] = request.build_absolute_uri(url)
            else:
                data['profile_picture'] = url
        else:
            # Puedes poner aquí la URL de un ícono por defecto si lo deseas
            data['profile_picture'] = None
        return data

    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("El nombre de usuario ya está en uso.")
        return value

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    otp_code = serializers.CharField(required=False)

    def validate(self, attrs):

        return attrs
