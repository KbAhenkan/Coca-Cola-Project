from .models import User, Product, Order, OrderItem
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only':True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock']


class OrderSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'date']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model =  OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price_at_purchase']