from django.contrib import admin
from .models import StockMoviment

@admin.register(StockMoviment)
class StockMovimentAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'movement_type', 'date')
    list_filter = ('movement_type', 'date')
    search_fields = ('product__title',)
