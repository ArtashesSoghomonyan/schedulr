import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import (
    FORBIDDEN_USERNAMES,
    CostumerProfile,
    DeletedUserEmail,
    ProviderProfile,
    User,
)


class CostumerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostumerProfile
        fields = ("user", "first_name", "last_name")
        read_only_fields = ("user",)

class ProviderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderProfile
        fields = ("user", "business_name", "description", "slug")
        read_only_fields = ("user", "slug")

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "user_type", "profile", "is_verified")
        read_only_fields = ("username", "email", "user_type", "is_verified")

    def get_profile(self, obj: User):
        if obj.user_type == User.UserType.PROVIDER:
            if hasattr(obj, "provider_profile"):
                return ProviderProfileSerializer(obj.provider_profile).data
        elif obj.user_type == User.UserType.COSTUMER:
            if hasattr(obj, "costumer_profile"):
                return CostumerProfileSerializer(obj.costumer_profile).data
        return None

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "user_type")
        read_only_fields = ("username", "user_type")

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.EmailField()
        self.fields.pop("username", None)

    def validate(self, attrs):
        attrs[self.username_field] = attrs.pop("email")
        return super().validate(attrs)

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, max_length=50)
    password = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(choices=User.UserType.choices)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        elif DeletedUserEmail.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email was deleted. You cannot use this email."
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        if not re.fullmatch(r"^[a-z_]+$", value):
            raise serializers.ValidationError(
                "Username must be lowercase letters or underscores only"
            )
        if value in FORBIDDEN_USERNAMES:
            raise serializers.ValidationError(
                "Username is not available"
            )
        return value

    def validate_password(self, value):
        """
        Validate password strength. User is not passed because the user
        doesn't exist yet — similarity checks (email in password, etc.)
        are intentionally skipped at registration.
        """
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user
