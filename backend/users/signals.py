from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.text import slugify

from users.models import DeletedUserEmail, User


@receiver(pre_delete, sender=User)
def create_deleted_email_instance(sender, instance, **kwargs):
    if instance.is_verified:
        DeletedUserEmail.objects.create(email=instance.email)
