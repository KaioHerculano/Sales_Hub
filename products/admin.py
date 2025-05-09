from django.contrib import admin
from .models import Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'serie_number',)
    search_fields = ('title', 'serie_number')


admin.site.register(Product, ProductAdmin)
