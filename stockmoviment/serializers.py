from rest_framework import serializers
from .models import StockMoviment


class StockMovimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMoviment
        fields = '__all__'
