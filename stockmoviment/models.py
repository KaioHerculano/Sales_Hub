from django.db import models
from companies.models import Company


class StockMoviment(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Entrada'),
        ('out', 'Saída'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name='Tipo de Movimentação')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} de {self.quantity} unidades - {self.product.title}"

    class Meta:
        verbose_name = 'Histórico de Estoque'
        verbose_name_plural = 'Históricos de Estoque'
