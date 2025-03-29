from django.contrib import admin
from .models import Sale, SaleItem, Product


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale_date', 'total', 'discount',)
    inlines = [SaleItemInline]
    readonly_fields = ('total',)

admin.site.register(Sale, SaleAdmin)