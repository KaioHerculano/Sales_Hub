from django.contrib import admin
from .models import Sale, SaleItem, Order, Budget


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    min_num = 1
    fields = ('product', 'quantity', 'unit_price', 'subtotal')
    readonly_fields = ('subtotal',)



class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale_date', 'client', 'seller', 'total', 'discount', 'sale_type', 'order_status')
    list_filter = ('sale_date', 'sale_type', 'order_status')
    search_fields = ('id', 'client__name')
    inlines = [SaleItemInline]
    readonly_fields = ('total', 'sale_date')
    
    fieldsets = (
        (None, {
            'fields': ('client', 'seller', 'sale_type', 'order_status')
        }),
        ('Valores', {
            'fields': ('discount', 'total')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.sale_type == 'quote':
            return readonly_fields + ('sale_type', 'order_status')
        return readonly_fields


class OrderAdmin(SaleAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(sale_type='order')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.order_status == 'finalized':
            return readonly_fields + ('client', 'discount')
        return readonly_fields


class BudgetAdmin(SaleAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(sale_type='quote')

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        field = super().formfield_for_choice_field(db_field, request, **kwargs)
        if db_field.name == 'order_status':
            field.choices = [
                choice for choice in field.choices
                if choice[0] not in ['finalized', 'delivered', 'sent', 'waiting']
            ]
        return field

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            return readonly_fields + ('sale_type',)
        return readonly_fields



admin.site.register(Sale, SaleAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Budget, BudgetAdmin)