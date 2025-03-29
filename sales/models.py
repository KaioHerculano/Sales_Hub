from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.conf import settings

from products.models import Product  
from clients.models import Client  

class Sale(models.Model):
    sale_date = models.DateTimeField("Data da Venda", auto_now_add=True)
    total = models.DecimalField("Total da Venda", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField("Desconto (%)", max_digits=5, decimal_places=2, default=Decimal("0.00"),
                                   validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))],
                                   help_text="Informe o desconto em porcentagem")
    client = models.ForeignKey(Client, verbose_name="Cliente", on_delete=models.SET_NULL, null=True, blank=True)
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Caixa", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-sale_date']

    def __str__(self):
        return f"Venda {self.id} - {self.sale_date:%d/%m/%Y %H:%M}"

    def calculate_total(self):
        subtotal = sum(item.subtotal() for item in self.items.all())
        discount_value = subtotal * (self.discount / Decimal("100.00"))
        self.total = subtotal - discount_value
        self.save(update_fields=["total"])
        return self.total


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE, verbose_name="Venda")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Produto")
    quantity = models.PositiveIntegerField("Quantidade", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField("Preço Unitário", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])

    class Meta:
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens das Vendas"

    def __str__(self):
        return f"{self.product.title} - {self.quantity} x R$ {self.unit_price:.2f}"

    def subtotal(self):
        return self.quantity * self.unit_price
