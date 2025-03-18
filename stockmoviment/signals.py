from django.db.models.signals import post_save
from django.dispatch import receiver
from outflows.models import Outflow
from inflows.models import Inflow
from .models import StockMoviment

@receiver(post_save, sender=Inflow)
def update_stock_on_inflow(sender, instance, created, **kwargs):
    if created:  
        product = instance.product
        StockMoviment.objects.create(
            product=product,
            quantity=instance.quantity,
            movement_type='in'
        )

@receiver(post_save, sender=Outflow)
def update_stock_on_outflow(sender, instance, created, **kwargs):
    if created:  
        product = instance.product
        StockMoviment.objects.create(
            product=product,
            quantity=instance.quantity,
            movement_type='out'
        )