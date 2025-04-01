from rest_framework import serializers
from .models import Sale, SaleItem

class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'quantity', 'unit_price']
        extra_kwargs = {
            'product': {'required': True},
            'quantity': {'min_value': 1},
            'unit_price': {'min_value': 0}
        }

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ('total', 'sale_date')
        extra_kwargs = {
            'discount': {'min_value': 0, 'max_value': 100},
            'cashier': {'required': False}
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sale = Sale.objects.create(**validated_data)
        for item_data in items_data:
            SaleItem.objects.create(sale=sale, **item_data) 
        sale.calculate_total()
        return sale

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                SaleItem.objects.create(sale=instance, **item_data)
            instance.calculate_total()
        return instance