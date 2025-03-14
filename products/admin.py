from django.contrib import admin
from .models import Product, StockHistory


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'serie_number', 'numbering')
    search_fields = ('title', 'numbering', 'serie_number')

admin.site.register(Product, ProductAdmin)

@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'movement_type', 'date')
    list_filter = ('movement_type', 'date')
    search_fields = ('product__title',)