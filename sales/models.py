from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from decimal import Decimal
from django.conf import settings
from products.models import Product
from clients.models import Client


class Seller(models.Model):
    name = models.CharField("Seller Name", max_length=255)

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    name = models.CharField("Payment Method", max_length=255)

    def __str__(self):
        return self.name


PAYMENT_METHOD_CHOICES = [
    ('cash', 'Dinheiro'),
    ('card', 'Cartão'),
    ('pix', 'Pix'),
    ('boleto', 'Boleto'),
]


class Sale(models.Model):
    sale_date = models.DateTimeField("Sale Date", auto_now_add=True)
    total = models.DecimalField("Sale Total", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField("Discount (%)", max_digits=5, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))], help_text="Enter the discount percentage")
    client = models.ForeignKey(Client, verbose_name="Client", on_delete=models.SET_NULL, null=True, blank=True)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Cashier", related_name="sales_as_cashier", on_delete=models.SET_NULL, null=True, blank=True)
    seller = models.ForeignKey(User, verbose_name="Seller", on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField("Payment Method", max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        ordering = ['-sale_date']

    def __str__(self):
        return f"Sale {self.id} - {self.sale_date:%d/%m/%Y %H:%M}"

    def calculate_total(self):
        subtotal = sum(item.subtotal() for item in self.items.all())
        discount_value = subtotal * (self.discount / Decimal("100.00"))
        self.total = subtotal - discount_value
        self.save(update_fields=["total"])
        return self.total


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE, verbose_name="Sale")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Product")
    quantity = models.PositiveIntegerField("Quantity", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField("Unit Price", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    purchase_price = models.DecimalField("Purchase Price", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])

    class Meta:
        verbose_name = "Sale Item"
        verbose_name_plural = "Sale Items"

    def __str__(self):
        return f"{self.product.title} - {self.quantity} x R$ {self.unit_price:.2f}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.purchase_price = self.product.cost_price
        super().save(*args, **kwargs)

    def subtotal(self):
        return self.quantity * self.unit_price
