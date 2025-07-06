from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(read_only=True, slug_field='name')
    brand = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Product
        fields = '__all__'
