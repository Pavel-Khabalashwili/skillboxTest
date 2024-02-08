from rest_framework import serializers
from .models import Product


class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "sku",
            "name",
            "category",
            "quantity",
            "price"
        )

    def validate_price(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise serializers.ValidationError("Цена должна быть числом и больше 0.")
        return value