from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Budget

@receiver(pre_save, sender=Budget)
def check_expiration(sender, instance, **kwargs):
    if instance.expiration_date and instance.expiration_date < timezone.now().date():
        raise ValidationError("Orçamento expirado não pode ser alterado.")