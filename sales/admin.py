from django.contrib import admin
from .models import Sale, SaleItem, Order, Budget


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale_date', 'total', 'discount',)
    inlines = [SaleItemInline]
    readonly_fields = ('total',)


class OrderAdmin(SaleAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(sale_type='order')
    
class BudgetAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.sale_type == 'quote':
            # Remove 'finalized' das opções de status
            status_field = form.base_fields['order_status']
            status_field.choices = [
                choice for choice in status_field.choices
                if choice[0] != 'finalized'
            ]
        return form


admin.site.register(Sale, SaleAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Budget, BudgetAdmin)
