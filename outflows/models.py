from django.db import models
from products.models import Product
from django.contrib.auth.models import User


class Outflow(models.Model):
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

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='outflows', verbose_name="Produto")
    quantity = models.PositiveIntegerField("Quantidade")
    numbering = models.CharField("Numeração", max_length=50, blank=True, null=True)
    sale_reference = models.CharField("Referência da Venda", max_length=100, blank=True, null=True)
    description = models.TextField("Descrição", blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField("Criado Em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado Em", auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.product.title
