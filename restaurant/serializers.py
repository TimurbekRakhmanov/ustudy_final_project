# posts/serializers.py
from rest_framework import serializers
from .models import Restaurant, User, Client, Category, Dish, Ingredient, RecipeItem, Table, Order, OrderItem, Reservation, StockTransaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.utils import timezone
from django.db import transaction

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('name', 'address', 'phone', 'is_active', 'logo')
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password',  'role', 'phone', 'is_active')
        
        
class ClientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    phone = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'phone')

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password'],
                phone=validated_data['phone'],
                role='client'  
            )
            Client.objects.create(user=user)
            
            return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'phone': self.user.phone,
            'role': self.user.role,
        }
        return data
    
    
    

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'        
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields= ("name", 'order_index')
        


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model=Dish
        fields=('name', 'description', 'price', 'is_available', 'logo', 'category')
        
        
class DishStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ['is_available']

  
        
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model=Ingredient
        fields=('name', 'unit', 'current_stock')
        
        
  
class StockTransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransaction
        fields = ('type', 'quantity', 'reason')

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Muqdari 0 den ulken bolwy kerek!")
        return value
  
  
  
  
    
class RecipeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=RecipeItem
        fields = ('id', 'quantity_per_serving', 'dish', 'ingredient')
        


        


class StockTransaction(serializers.ModelSerializer):
    class Meta:
        model=Table
        fields=('type', 'quantity', 'reason', 'created_at')


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model=Table
        fields=('number', 'seats_count', 'status_is_free')
    


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        # fields='__all__'
        fields=('payment_method', 'status', 'created_at', 'closed_at', 'waiter', 'client', 'table')
        

        
        
class StatusOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=('status', 'payment_method')
        #read_only_fields = ['table', 'waiter', 'client']
        
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields=('dish','quantity', 'note', 'status', 'order')
        read_only_fields = ('order',)
        
        
class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('id', 'datetime', 'guests_count', 'status', 'client', 'restaurant', 'table')

    def validate_datetime(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Rezerv waqti otken zamanda boliwi mumkin emes!")
        return value   
        
        


        
