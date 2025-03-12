from django.contrib import admin
from . import models


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'serie_number', 'numbering',)
    search_fields = ('title', 'numbering', 'serie_number',)


admin.site.register(models.Product, ProductAdmin)