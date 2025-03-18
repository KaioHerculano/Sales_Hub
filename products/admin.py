from django.contrib import admin
from .models import Product 


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'serie_number', 'numbering')
    search_fields = ('title', 'numbering', 'serie_number')

admin.site.register(Product, ProductAdmin)
