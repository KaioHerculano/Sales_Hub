# Generated by Django 5.1.6 on 2025-04-20 06:30

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        ('companies', '0001_initial'),
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Payment Method')),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Seller Name')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_date', models.DateTimeField(auto_now_add=True, verbose_name='Sale Date')),
                ('total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name='Sale Total')),
                ('discount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Enter the discount percentage', max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00')), django.core.validators.MaxValueValidator(Decimal('100.00'))], verbose_name='Discount (%)')),
                ('payment_method', models.CharField(blank=True, choices=[('cash', 'Dinheiro'), ('card', 'Cartão'), ('pix', 'Pix'), ('boleto', 'Boleto')], max_length=20, null=True, verbose_name='Payment Method')),
                ('sale_type', models.CharField(choices=[('order', 'Pedido de Venda'), ('quote', 'Orçamento')], default='order', max_length=5, verbose_name='Tipo de Venda')),
                ('order_status', models.CharField(blank=True, choices=[('draft', 'Rascunho'), ('pending', 'Pendente'), ('waiting', 'Aguardando pagamento'), ('finalized', 'Finalizado'), ('canceled', 'Cancelado'), ('delivered', 'Entregue'), ('sent', 'Enviado'), ('approved', 'Aprovado'), ('rejected', 'Rejeitado')], default='finalized', max_length=20, null=True, verbose_name='Status')),
                ('expiration_date', models.DateField(blank=True, help_text='Data de expiração do orçamento (aplicável apenas para orçamentos)', null=True, verbose_name='Data de Validade')),
                ('cashier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_as_cashier', to=settings.AUTH_USER_MODEL, verbose_name='Cashier')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.client', verbose_name='Client')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company')),
                ('seller', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Seller')),
            ],
            options={
                'verbose_name': 'Sale',
                'verbose_name_plural': 'Sales',
                'ordering': ['-sale_date'],
            },
        ),
        migrations.CreateModel(
            name='Budget',
            fields=[
            ],
            options={
                'verbose_name': 'Orçamento',
                'verbose_name_plural': 'Orçamentos',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sales.sale',),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
            ],
            options={
                'verbose_name': 'Pedido de Venda',
                'verbose_name_plural': 'Pedidos de Venda',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sales.sale',),
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Quantity')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Unit Price')),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Purchase Price')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product', verbose_name='Product')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='sales.sale', verbose_name='Sale')),
            ],
            options={
                'verbose_name': 'Sale Item',
                'verbose_name_plural': 'Sale Items',
            },
        ),
    ]
