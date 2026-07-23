from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
    ValidationError,
)
from django.db import models
from django.utils.text import slugify

FORBIDDEN_USERNAMES = [
    "signup",
    "profile",
    "settings",
]

def validate_username_not_forbidden(value: str):
    if value.lower() in FORBIDDEN_USERNAMES:
        raise ValidationError(
            "This username is not allowed.",
            code="forbidden_username",
        )

def validate_is_alpha(value: str):
    if not value.isalpha():
        raise ValidationError("This field may contain only letters.")

def deleted_email_validator(value: str):
    if DeletedUserEmail.objects.filter(email=value).exists():
        raise ValidationError(
            "This email cannot be used, because it has been used before."
        )


class User(AbstractUser):
    class UserType(models.TextChoices):
        PROVIDER = "Provider"
        COSTUMER = "Costumer"

    username = models.CharField(max_length=50, unique=True, validators=[RegexValidator(r"^[a-z_]+$"), MinLengthValidator(3), MaxLengthValidator(50), validate_username_not_forbidden], db_index=True)
    email = models.EmailField(unique=True, validators=[deleted_email_validator])
    user_type = models.CharField(max_length=10, choices=UserType.choices)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return f"{self.email} ({self.user_type})"


class DeletedUserEmail(models.Model):
    email = models.EmailField(unique=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.email)


class ProviderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="provider_profile")
    business_name = models.CharField(max_length=250, validators=[MinLengthValidator(4), MaxLengthValidator(250)])
    description = models.TextField(blank=True)
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        self.slug = f"{slugify(self.business_name)}-{self.id * 3}"
        super().save(*args, **kwargs)

    # TODO: phone number field
    # TODO: business types and tags
    # TODO: Images + avatar

    def __str__(self) -> str:
        return str(self.business_name)


class CostumerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="costumer_profile")
    first_name = models.CharField(max_length=30, validators=[validate_is_alpha])
    last_name = models.CharField(max_length=30, validators=[validate_is_alpha])
    # TODO: phone number field
    # TODO: avatar

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
