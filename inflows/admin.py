from django.contrib import admin
from . import models


class InflowAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'numbering', 'created_at', 'updated_at')
    search_fields = ('product__name', 'numbering', 'product__title',)


admin.site.register(models.Inflow, InflowAdmin)
