
    
from rest_framework import viewsets, generics, serializers, status
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import F
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Restaurant, User, Client, Category, Dish, Ingredient, RecipeItem, Table, Order, OrderItem, Reservation

from .serializers import (StatusOrderSerializer,StockTransactionCreateSerializer, DishStatusSerializer, RestaurantSerializer, UserSerializer, ClientSerializer, 
                          CategorySerializer, DishSerializer, IngredientSerializer, RecipeItemSerializer, TableSerializer, 
                          OrderItemSerializer, OrderSerializer, ReservationSerializer, ClientRegistrationSerializer, CustomTokenObtainPairSerializer)

from .permissions import (PermissionRestaurat, PermissionUser, PermissionCategory, PermissionDish, PermissionDishStatus, 
                          PermissionIngredient, PermissionTable, PermissionOrder, PermissionActiveOrderItem, PermissionChangeOrderStatus, 
                          PermissionRecipe, PermissionReservation, PermissionReservationForClient)






@extend_schema(tags=['Registration only for clients'])
class ClientRegisterView(generics.CreateAPIView):
    serializer_class = ClientRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "message": "Klient dizimnen ótkerildi",
            "user": {
                "id": user.id,
                "username": user.username,
                "phone": user.phone,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['all registred users can get token']) 
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



@extend_schema(tags=['Logging out only for clients'])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token kerek."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Sistemadan shiqtiniz!"}, 
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError:
            return Response(
                {"detail": "Qate yamasa muddteti otken token."}, 
                status=status.HTTP_400_BAD_REQUEST
            )





class RestaurantBaseView:
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated, PermissionRestaurat]

    def get_queryset(self):
        user = self.request.user
        
        if user.is_superuser or Client.objects.filter(user=user).exists():
            return Restaurant.objects.all()
        
        if hasattr(user, 'restaurant') and user.restaurant:
            return Restaurant.objects.filter(id=user.restaurant.id)
        
        return Restaurant.objects.none()
    
    

@extend_schema(tags=['Restaurants (any user can get list, only superuser can create)'])
class RestaurantListCreateView(RestaurantBaseView, generics.ListCreateAPIView):
    pass



@extend_schema(tags=['Restaurant detail page (superuser can do anything, others only read)'])
class RestaurantRetrieveUpdateDestroyView(RestaurantBaseView, generics.RetrieveUpdateDestroyAPIView):
    pass    


@extend_schema(tags=['Users (restaurant-staff can only read, only admin and superadmin can create)'])      
class UserListCreateView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [PermissionUser, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user  
        queryset = User.objects.select_related('restaurant')

        if user.is_superuser:
            return queryset.all()

        user_restaurant_id = getattr(user, 'restaurant_id', None)
        if user_restaurant_id:
            return queryset.filter(restaurant_id=user_restaurant_id)
            
        return User.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        
        if user.is_superuser:
            serializer.save()
        else:
            user_restaurant_id = getattr(user, 'restaurant_id', None)
            if not user_restaurant_id:
                raise serializers.ValidationError({"restaurant": "Admin restoranga biriktirilmegen"})
            
            serializer.save(restaurant_id=user_restaurant_id)
      


@extend_schema(tags=['Users detail page (restaurant-staff can only read, admin and superuser can do anything)'])
class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [PermissionUser, IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.select_related('restaurant')

        if user.is_superuser:
            return queryset.all()

        if user.restaurant_id:
            if user.role == 'admin':
                return queryset.filter(restaurant_id=user.restaurant_id)
            else:
                return queryset.filter(id=user.id)

        return queryset.none()









    
    

@extend_schema(tags=['Category (restaurant-staff, clients can only read, only admin and superadmin can create)'])
class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class=CategorySerializer
    permission_classes=[PermissionCategory,IsAuthenticated]
    
    def get_queryset(self):
            user = self.request.user
            restaurant_id = self.kwargs.get('pk')
            queryset = Category.objects.select_related('restaurant')
            
            is_client = hasattr(user, 'client') 

            if user.is_superuser or is_client:
                return queryset.filter(restaurant_id=restaurant_id)
            
            if user.restaurant_id:
                return queryset.filter(restaurant_id=user.restaurant_id)  
                
            return queryset.none()
        
    def perform_create(self, serializer):
            user = self.request.user

            if user.is_superuser:
                restaurant_pk = self.kwargs.get('pk')
                if restaurant_pk:
                    serializer.save(restaurant_id=restaurant_pk)
                else:
                    serializer.save()

            elif user.restaurant_id:
                serializer.save(restaurant_id=user.restaurant_id)

            else:
                raise PermissionDenied(
                    'Siz esh qaysi restoranga biriktirilmegensiz!'
                )
        



@extend_schema(tags=['Dish (restaurant-staff, clients can only read, only admin and superadmin can create)'])
class DishListCreateView(generics.ListCreateAPIView):
    serializer_class=DishSerializer
    permission_classes=[PermissionDish,IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user                             
        restaurant_id = self.kwargs.get('pk')
        queryset = Dish.objects.select_related('restaurant', 'category')
        is_client = hasattr(user, 'client')
        
        if user.is_superuser or is_client:
            return queryset.filter(restaurant_id=restaurant_id)
        
        if user.restaurant_id:
            return queryset.filter(restaurant_id=user.restaurant_id)
        return queryset.none() 
    
    def perform_create(self, serializer):
            user = self.request.user

            if user.is_superuser:
                restaurant_pk = self.kwargs.get('pk')
                if restaurant_pk:
                    serializer.save(restaurant_id=restaurant_pk)
                else:
                    serializer.save()

            elif user.restaurant_id:
                serializer.save(restaurant_id=user.restaurant_id)

            else:
                raise PermissionDenied(
                    'Siz esh qaysi restoranga biriktirilmegensiz!'
                )





@extend_schema(tags=['Dish status (any staff user can change status of dish)'])
class DishStatusChangeView(generics.UpdateAPIView):
    serializer_class = DishStatusSerializer
    permission_classes = [PermissionDishStatus, IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Dish.objects.select_related('restaurant')
        
        if user.is_superuser:
            return queryset
        
        if user.restaurant_id:
            return queryset.filter(restaurant_id=user.restaurant_id)
            
        return queryset.none()



    

@extend_schema(tags=['Igridients (only admin, storekeeper and superadmin can create, other restaurant-staff can only read)'])
class IngredientListCreateView(generics.ListCreateAPIView):
    serializer_class=IngredientSerializer
    permission_classes=[PermissionIngredient,IsAuthenticated]
   
    def get_queryset(self):
        user = self.request.user    
        restaurant_id = self.kwargs.get('pk')
        queryset = Ingredient.objects.all()
        
        if user.is_superuser:
            if restaurant_id:
                return queryset.filter(restaurant_id=restaurant_id) 
            return queryset
                 
        if getattr(user, 'restaurant_id', None):
            return queryset.filter(restaurant_id=user.restaurant_id)

        return queryset.none()
    
    

    def perform_create(self, serializer):
            user = self.request.user

            if user.is_superuser:
                restaurant_pk = self.kwargs.get('pk')
                if restaurant_pk:
                    serializer.save(restaurant_id=restaurant_pk)
                else:
                    raise serializers.ValidationError({'restaurant': 'ID resotandi URL da korsetin'})

            elif getattr(user, 'restaurant_id', None):
                serializer.save(restaurant_id=user.restaurant_id)

            else:
                raise PermissionDenied(
                    'Siz hesh qaysi restoranga biriktirilmegensiz!'
                )



@extend_schema(tags=['Ingredients (only admin, storekeeper and superadmin can add, others only read)'])
class IngredientAddView(generics.UpdateAPIView):
    serializer_class = StockTransactionCreateSerializer
    permission_classes = [PermissionIngredient, IsAuthenticated]
   
    def get_queryset(self):
        user = self.request.user
        queryset = Ingredient.objects.all()  
        
        if user.is_superuser:
            return queryset
        
        if getattr(user, 'restaurant_id', None):
            return queryset.filter(restaurant_id=user.restaurant_id)
       
        return queryset.none()
    
    @transaction.atomic  
    def perform_update(self, serializer):
        ingredient = self.get_object()
        stock_transaction = serializer.save(ingredient=ingredient)

        if stock_transaction.type == 'kirim':
            Ingredient.objects.filter(pk=ingredient.pk).update(
                current_stock=F('current_stock') + stock_transaction.quantity
            )
        elif stock_transaction.type == 'shigim':
            Ingredient.objects.filter(pk=ingredient.pk).update(
                current_stock=F('current_stock') - stock_transaction.quantity
            )
    
    
    
@extend_schema(tags=['Tables (only admin, waiter and superadmin can create, others only read)'])
class TableListCreateView(generics.ListCreateAPIView):
    serializer_class = TableSerializer
    permission_classes = [PermissionTable, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        restaurant_pk = self.kwargs.get('pk')
        queryset = Table.objects.all()

        if user.is_superuser:
            if restaurant_pk:
                return queryset.filter(restaurant_id=restaurant_pk)
            return queryset

        if getattr(user, 'restaurant_id', None):
            return queryset.filter(restaurant_id=user.restaurant_id)

        if hasattr(user, 'client'):
            queryset = queryset.filter(status_is_free=True)
            if restaurant_pk:
                queryset = queryset.filter(restaurant_id=restaurant_pk)
            return queryset

        return Table.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_superuser:
            restaurant_pk = self.kwargs.get('pk')
            if not restaurant_pk:
                raise serializers.ValidationError({'restaurant': 'Resotan ID URL de korsetilmegen'})
            serializer.save(restaurant_id=restaurant_pk)

        elif getattr(user, 'restaurant_id', None):
            serializer.save(restaurant_id=user.restaurant_id)

        else:
            raise PermissionDenied('Siz hech qaysi restoranga biriktirilmagansiz!')



@extend_schema(tags=['Tables (only admin, waiter and superadmin can update, delete, others only read)'])
class TableDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TableSerializer
    permission_classes = [PermissionTable, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Table.objects.all()

        if user.is_superuser:
            return queryset

        if getattr(user, 'restaurant_id', None):
            return queryset.filter(restaurant_id=user.restaurant_id)

        return Table.objects.none()

       

@extend_schema(tags=['Orders (only admin, waiter and superadmin can create, others only read)'])   
class OrderListCreateView (generics.ListCreateAPIView): 
    serializer_class=OrderSerializer
    permission_classes=[PermissionOrder,IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        queryset = Order.objects.all()
        if user.is_superuser:
            return queryset

        if getattr(user, 'restaurant_id', None):
            return queryset.filter(table__restaurant_id=user.restaurant_id)

        if hasattr(user, 'client'):
            return queryset.filter(client__user=user)

        return queryset.none()


        
        
@extend_schema(tags=['Active order items (only read)'])     
class ActiveOrderItemListView(generics.ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [PermissionActiveOrderItem, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
    
        queryset = OrderItem.objects.filter(status='active').select_related(
            'dish', 
            'order__table'
        )
        if user.is_superuser:
            return queryset
        restaurant_id = getattr(user, 'restaurant_id', None)
        if restaurant_id:
            if getattr(user, 'role', None) in ['chef', 'admin']:
                return queryset.filter(order__table__restaurant_id=restaurant_id)
            
            if getattr(user, 'role', None) == 'waiter':
                return queryset.filter(
                    order__table__restaurant_id=restaurant_id, 
                    order__waiter_id=user.id
                )

        return OrderItem.objects.none()

@extend_schema(tags=['Active order items (only admin, chef and superadmin can update, others only read)'])         
class ActiveOrderItemUpdateView(generics.UpdateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [PermissionActiveOrderItem, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = OrderItem.objects.select_related('dish', 'order__table')

        if user.is_superuser:
            return queryset

        restaurant_id = getattr(user, 'restaurant_id', None)
        if restaurant_id and getattr(user, 'role', None) in ['chef', 'admin']:
            return queryset.filter(order__table__restaurant_id=restaurant_id)

        return OrderItem.objects.none()



@extend_schema(tags=['Order status (only admin, superadmin can update, others only read)'])   
class ChangeOrdersStatusView(generics.UpdateAPIView):
    serializer_class = StatusOrderSerializer
    permission_classes = [IsAuthenticated, PermissionChangeOrderStatus]

    def get_queryset(self):
        user = self.request.user 
        
        queryset = Order.objects.filter(status='active').select_related('table')

        if user.is_superuser:
            return queryset
        
        if hasattr(user, 'restaurant') and user.restaurant:
            return queryset.filter(table__restaurant=user.restaurant)
            
        return Order.objects.none()  

    def perform_update(self, serializer):
        new_status = serializer.validated_data.get('status')

        if new_status == 'closed':
            order = serializer.save(closed_at=timezone.now())
        else:
            order = serializer.save()

        if order.status == 'closed':
            table = order.table 
            if table and not table.status_is_free:
                table.status_is_free = True
                table.save(update_fields=['status_is_free'])
                    
                    
                    
                    
@extend_schema(tags=['Order items (only admin, superadmin, waiter can create, others only read)'])  
class OrderItemViewSet(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, PermissionOrder]
    
    def get_queryset(self):
        user = self.request.user
        order_pk = self.kwargs.get('order_pk')

        base_qs = OrderItem.objects.select_related('dish', 'order')

        if user.is_superuser:
            return base_qs.all()
            
        if hasattr(user, 'restaurant') and user.restaurant:
            return base_qs.filter(order_id=order_pk)
            
        return base_qs.filter(order__client__user=user, order_id=order_pk)

    def perform_create(self, serializer):
        order_id = self.kwargs.get('order_pk')

        if not Order.objects.filter(pk=order_id).exists():
            raise NotFound("Заказ не найден")
            
        serializer.save(order_id=order_id)
    
    





@extend_schema(tags=['RecipeItem (only admin, superadmin, storekeeper can create, others only read)'])   
class RecipeItemViewSet(generics.ListCreateAPIView):
    serializer_class = RecipeItemSerializer
    permission_classes = [IsAuthenticated, PermissionRecipe]

    def get_queryset(self):
        user = self.request.user
        base_qs = RecipeItem.objects.select_related('dish', 'ingredient')

        if user.is_superuser:
            restaurant_pk = self.kwargs.get('pk')
            if restaurant_pk:
                return base_qs.filter(dish__restaurant_id=restaurant_pk)
            return base_qs.all()

        if hasattr(user, 'restaurant') and user.restaurant:
            return base_qs.filter(dish__restaurant=user.restaurant)

        restaurant_pk = self.kwargs.get('pk')
        if restaurant_pk:
            return base_qs.filter(dish__restaurant_id=restaurant_pk)

        return RecipeItem.objects.none()

    def perform_create(self, serializer):
        dish = serializer.validated_data.get('dish')
        ingredient = serializer.validated_data.get('ingredient')

        if dish.restaurant_id != ingredient.restaurant_id:
            raise ValidationError("Dish penen ingredient bir restoranga tiyisli boliw kerek!")

        serializer.save()


    



@extend_schema(tags=['RecipeItem (only admin, superadmin, storekeeper can update, others only read)']) 
class RecipeItemUpdateViewSet(generics.RetrieveUpdateAPIView):
    serializer_class = RecipeItemSerializer
    permission_classes = [IsAuthenticated, PermissionRecipe]
    lookup_url_kwarg = 'item_pk'

    def get_queryset(self):
        user = self.request.user
        restaurant_pk = self.kwargs.get('pk')
        base_qs = RecipeItem.objects.select_related('dish', 'ingredient')
        user_role = getattr(user, 'role', None)

        if user.is_superuser or user_role in ['admin', 'storekeeper']:
            if restaurant_pk:
                return base_qs.filter(dish__restaurant_id=restaurant_pk)
                
        user_restaurant_id = getattr(user, 'restaurant_id', None)
        if user_restaurant_id:
            return base_qs.filter(dish__restaurant_id=user_restaurant_id)

        return RecipeItem.objects.none()

    
    
    
    
@extend_schema(tags=['Reservation (only admin, superadmin, clients can create, others only read)'])   
class ReservationListCreateView(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, PermissionReservation]

    def get_queryset(self):
        user = self.request.user
        restaurant_pk = self.kwargs.get('pk')
        base_qs = Reservation.objects.select_related('client', 'restaurant', 'table')

        if user.is_superuser:
            if restaurant_pk:
                return base_qs.filter(restaurant_id=restaurant_pk)
            return base_qs.all()

        user_role = getattr(user, 'role', None)

        if user_role == 'client':
            return base_qs.filter(client__user_id=user.id)

        if user_role == 'admin':
            user_restaurant_id = getattr(user, 'restaurant_id', None)
            if user_restaurant_id:
                return base_qs.filter(restaurant_id=user_restaurant_id)
            return base_qs.none()

        return base_qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        restaurant_pk = self.kwargs.get('pk')
        user_role = getattr(user, 'role', None)

        if user.is_superuser:
            serializer.save()
            return

        if user_role == 'client':
            client_id = getattr(user, 'client_id', None) or getattr(user.client, 'id', None)
            
            if not restaurant_pk:
                raise serializers.ValidationError({"restaurant": "ID restoran URL da korsetilmegen."})
            
            serializer.save(restaurant_id=restaurant_pk, client_id=client_id)

        elif user_role == 'admin':
            user_restaurant_id = getattr(user, 'restaurant_id', None)
            if not user_restaurant_id:
                raise serializers.ValidationError({"detail": "Bul admin restoranga biriktirilmegen."})
            serializer.save(restaurant_id=user_restaurant_id)
        else:
            raise serializers.ValidationError({"detail": "Sizde bron qiliwga huquq joq"})
                



@extend_schema(tags=['Reservation  (List for clients)'])    
class ReservationListForClientView(generics.ListAPIView):
   
    serializer_class=ReservationSerializer
    permission_classes=[IsAuthenticated, PermissionReservationForClient]
    def get_queryset(self):
        user = self.request.user                  
        if user.role=='client':  
            return Reservation.objects.filter(client__user=user)
        return Reservation.objects.none() 

@extend_schema(tags=['Reservation (List for clients)'])    
class ReservationListForClientView(generics.ListAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, PermissionReservationForClient]

    def get_queryset(self):
        user = self.request.user                  
        if getattr(user, 'role', None) == 'client':  
            return Reservation.objects.select_related(
                'client', 
                'restaurant', 
                'table'
            ).filter(client__user_id=user.id)

        return Reservation.objects.none()
    




@extend_schema(tags=['ClientList']) 
class ClientListView(generics.ListAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user1 = self.request.user
        base_qs = Client.objects.select_related('user')

        if user1.is_superuser:
            return base_qs.filter(user__role='client')
        
        user_restaurant_id = getattr(user1, 'restaurant_id', None)
        if user_restaurant_id:
            return base_qs.filter(user__restaurant_id=user_restaurant_id).distinct()
        return base_qs.filter(user_id=user1.id)
        





@extend_schema(tags=['Client (detail page for clients)'])    
class ClientDetailPageView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Client.objects.all()
    serializer_class=ClientSerializer
    permission_classes=[IsAuthenticated]

    
    def get_object(self):
            try:
                return Client.objects.get(user=self.request.user)
            except Client.DoesNotExist:
                raise NotFound("Профиль клиента для данного пользователя не найден.")

