from django.db import models
from companies.models import Company
from products.models import Product
from django.contrib.auth.models import User


class Outflow(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='outflows', verbose_name="Produto")
    quantity = models.PositiveIntegerField("Quantidade")
    sale_reference = models.CharField("Referência da Venda", max_length=100, blank=True, null=True)
    description = models.TextField("Descrição", blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField("Criado Em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado Em", auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.product.title
