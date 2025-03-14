from django.db import models
from brands.models import Brand
from categories.models import Category


class Product(models.Model):
    NUMBERING_CHOICES = [
        ('34', '34'),
        ('35', '35'),
        ('36', '36'),
        ('37', '37'),
        ('38', '38'),
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
        ('43', '43'),
        ('44', '44'),
    ]

    title = models.CharField(max_length=300)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    quantity = models.IntegerField()
    numbering = models.CharField(max_length=2, choices=NUMBERING_CHOICES, null=True, blank=True)
    serie_number = models.CharField(max_length=300)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class StockHistory(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Entrada'),
        ('out', 'Saída'),
    ]

    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name='Tipo de Movimentação')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} de {self.quantity} unidades - {self.product.title}"

class Meta:
    verbose_name = 'Histórico de Estoque'
    Verbose_name_plural = 'HIstóricos de Estoque'