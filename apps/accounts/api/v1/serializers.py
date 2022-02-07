from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import serializers
from ....accounts.models import User
from ....profiles.api.v1.serializers import ProfileSerializer


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializes registration requests and creates a new user."""
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    referred = serializers.CharField(source='ref', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone', 'referred', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", ]


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    profile = ProfileSerializer(write_only=True)  # never expose profile information hence `write_only=True`
    first_name = serializers.CharField(source='profile.first_name', read_only=True)
    last_name = serializers.CharField(source='profile.last_name', read_only=True)

    class Meta:
        model = User
        # fields = ('email', 'password',)
        fields = ('phone', 'password', 'profile', 'first_name', 'last_name')
        # read_only_fields = ('token',)

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        password = validated_data.pop('password', None)
        profile_data = validated_data.pop('profile', {})

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)
        instance.save()

        for (key, value) in profile_data.items():
            setattr(instance.profile, key, value)
        instance.profile.save()
        return instance


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        "bad_token": "Token expired or invalid"
    }

    def validate(self, attrs):
        self.refresh = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.refresh).blacklist()
        except TokenError:
            self.fail('bad_token')
