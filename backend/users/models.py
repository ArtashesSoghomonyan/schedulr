from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
    ValidationError,
)
from django.db import models

FORBIDDEN_USERNAMES = [
    "signup",
    "profile",
    "settings",
]

def validate_username_not_forbidden(value):
    if value.lower() in FORBIDDEN_USERNAMES:
        raise ValidationError(
            "This username is not allowed.",
            code="forbidden_username",
        )

class User(AbstractUser):
    class UserType(models.TextChoices):
        PROVIDER = "Provider"
        CONSUMER = "Consumer"

    username = models.CharField(max_length=50, unique=True, validators=[RegexValidator(r"^[a-z_]+$"), MinLengthValidator(3), MaxLengthValidator(50), validate_username_not_forbidden], db_index=True)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=UserType.choices)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.user_type})"
