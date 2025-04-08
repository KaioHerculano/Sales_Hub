from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from decimal import Decimal
from django.conf import settings
from products.models import Product
from clients.models import Client
from django.utils import timezone


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

SALE_TYPE_CHOICES = [
    ('order', 'Pedido de Venda'),
    ('quote', 'Orçamento'),
]

ORDER_STATUS_CHOICES = [
    ('draft', 'Rascunho'),
    ('pending', 'Pendente'),
    ('waiting', 'Aguardando pagamento'),
    ('finalized', 'Finalizado'),
    ('canceled', 'Cancelado'),
    ('delivered', 'Entregue'),
    ('sent', 'Enviado'),
    ('approved', 'Aprovado'),
    ('rejected', 'Rejeitado'),
]


class Sale(models.Model):
    sale_date = models.DateTimeField("Sale Date", auto_now_add=True)
    total = models.DecimalField("Sale Total", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField("Discount (%)", max_digits=5, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))], help_text="Enter the discount percentage")
    client = models.ForeignKey(Client, verbose_name="Client", on_delete=models.SET_NULL, null=True, blank=True)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Cashier", related_name="sales_as_cashier", on_delete=models.SET_NULL, null=True, blank=True)
    seller = models.ForeignKey(User, verbose_name="Seller", on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField("Payment Method", max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    sale_type = models.CharField("Tipo de Venda", max_length=5, choices=SALE_TYPE_CHOICES, default='order')
    order_status = models.CharField("Status", max_length=20, choices=ORDER_STATUS_CHOICES, default='finalized', blank=True, null=True)
    expiration_date = models.DateField("Data de Validade", null=True, blank=True, help_text="Data de expiração do orçamento (aplicável apenas para orçamentos)")

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        ordering = ['-sale_date']

    def __str__(self):
        base = f"Sale {self.id} - {self.sale_date:%d/%m/%Y %H:%M}"
        if self.order_status:
            return f"{base} ({self.get_order_status_display()})"
        return base

    def calculate_total(self):
        subtotal = sum(item.subtotal() for item in self.items.all())
        discount_value = subtotal * (self.discount / Decimal("100.00"))
        self.total = subtotal - discount_value
        self.save(update_fields=["total"])
        return self.total

    def clean(self):
        if self.sale_type == 'quote' and self.order_status is None:
            raise ValidationError("Orçamentos precisam ter um status definido.")

        if self.sale_type == 'order' and self.order_status is None:
            raise ValidationError("Pedidos precisam ter um status definido.")

        if self.sale_type == 'quote' and not self.expiration_date:
            raise ValidationError("Orçamentos requerem uma data de validade.")


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE, verbose_name="Sale")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Product")
    quantity = models.PositiveIntegerField("Quantity", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField("Unit Price", max_digits=10, decimal_places=2,
                                     validators=[MinValueValidator(Decimal("0.00"))])
    purchase_price = models.DecimalField("Purchase Price", max_digits=10, decimal_places=2,
                                         validators=[MinValueValidator(Decimal("0.00"))])

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


class Order(Sale):
    class Meta:
        proxy = True
        verbose_name = "Pedido de Venda"
        verbose_name_plural = "Pedidos de Venda"


class BudgetManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(sale_type='quote')


class Budget(Sale):
    objects = BudgetManager()

    class Meta:
        proxy = True
        verbose_name = "Orçamento"
        verbose_name_plural = "Orçamentos"

    def save(self, *args, **kwargs):
        self.sale_type = 'quote'
        if not self.expiration_date:
            self.expiration_date = timezone.now().date() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    def convert_to_order(self):
        order = Order.objects.create(
            client=self.client,
            discount=self.discount,
            total=self.total,
            cashier=self.cashier,
            seller=self.seller,
            payment_method=self.payment_method,
            sale_type='order',
            order_status='draft',
        )
        for item in self.items.all():
            SaleItem.objects.create(
                sale=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price,
                purchase_price=item.purchase_price
            )

        self.order_status = 'converted'
        self.save(update_fields=['order_status'])

        order.calculate_total()
        return order
 