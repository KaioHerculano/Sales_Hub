from django.db import models
from companies.models import Company
from suppliers.models import Supplier
from products.models import Product


class Inflow(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='inflows')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='inflows')
    quantity = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return str(self.product)
