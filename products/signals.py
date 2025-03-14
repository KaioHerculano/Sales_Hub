# products/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from outflows.models import Outflow
from inflows.models import Inflow
from .models import StockHistory

@receiver(post_save, sender=Inflow)
def update_stock_on_inflow(sender, instance, created, **kwargs):
    if created:  
        product = instance.product
        product.quantity += instance.quantity
        product.save()
        StockHistory.objects.create(
            product=product,
            quantity=instance.quantity,
            movement_type='in'
        )

@receiver(post_save, sender=Outflow)
def update_stock_on_outflow(sender, instance, created, **kwargs):
    if created:  
        product = instance.product
        product.quantity -= instance.quantity
        product.save()
        StockHistory.objects.create(
            product=product,
            quantity=instance.quantity,
            movement_type='out'
        )

@receiver(post_delete, sender=Inflow)
def revert_stock_on_inflow_delete(sender, instance, **kwargs):
    product = instance.product
    product.quantity -= instance.quantity
    product.save()
    StockHistory.objects.create(
        product=product,
        quantity=instance.quantity,
        movement_type='out'
    )

@receiver(post_delete, sender=Outflow)
def revert_stock_on_outflow_delete(sender, instance, **kwargs):
    product = instance.product
    product.quantity += instance.quantity
    product.save()
    StockHistory.objects.create(
        product=product,
        quantity=instance.quantity,
        movement_type='in'
    )