
    
from rest_framework import viewsets, generics, serializers, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.exceptions import NotFound

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
        if user.is_superuser:
            return User.objects.all()
        if hasattr(user, 'restaurant') and user.restaurant:
            return User.objects.filter(restaurant=user.restaurant)
        return User.objects.none() 

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        else:
            serializer.save(restaurant=self.request.user.restaurant)
      
      


@extend_schema(tags=['Users detail page (restaurant-staff can only read, admin and superuser can do anything)'])
class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [PermissionUser, IsAuthenticated]
    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return User.objects.all()

        if hasattr(user, 'restaurant') and user.restaurant:
       
            if user.role == 'admin':
                return User.objects.filter(restaurant=user.restaurant)
            else:
                return User.objects.filter(id=user.id)

        return User.objects.none()









    
    

@extend_schema(tags=['Category (restaurant-staff, clients can only read, only admin and superadmin can create)'])
class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class=CategorySerializer
    permission_classes=[PermissionCategory,IsAuthenticated]
    
    def get_queryset(self):
            user = self.request.user
            restaurant_id = self.kwargs.get('pk')
            if user.is_superuser or Client.objects.filter(user=user).exists():
                    return Category.objects.filter(restaurant_id=restaurant_id)
            
            if hasattr(user, 'restaurant') and user.restaurant:
                    return Category.objects.filter(restaurant=user.restaurant)  
            return Category.objects.none()   
        
    # def perform_create(self, serializer):
    #     restaurant_pk = self.kwargs.get('pk')
    #     serializer.save(restaurant_id=restaurant_pk)
        
    def perform_create(self, serializer):
            user = self.request.user

            if user.is_superuser:
                restaurant_pk = self.kwargs.get('pk')
                if restaurant_pk:
                    serializer.save(restaurant_id=restaurant_pk)
                else:
                    serializer.save()

            elif hasattr(user, 'restaurant') and user.restaurant:
                serializer.save(restaurant=user.restaurant)

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
        
        if user.is_superuser or Client.objects.filter(user=user).exists():
            return Dish.objects.filter(restaurant_id=restaurant_id)
        
        if hasattr(user, 'restaurant') and user.restaurant:
            return Dish.objects.filter(restaurant=user.restaurant)

        return Dish.objects.none()   
    
    # def perform_create(self, serializer):
    #     restaurant_pk = self.kwargs.get('pk')
    #     serializer.save(restaurant_id=restaurant_pk)
    
    def perform_create(self, serializer):
            user = self.request.user

            if user.is_superuser:
                restaurant_pk = self.kwargs.get('pk')
                if restaurant_pk:
                    serializer.save(restaurant_id=restaurant_pk)
                else:
                    serializer.save()

            elif hasattr(user, 'restaurant') and user.restaurant:
                serializer.save(restaurant=user.restaurant)

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
        
        if hasattr(user, 'restaurant') and user.restaurant:
            return Dish.objects.filter(restaurant=user.restaurant)
            
        return Dish.objects.none()



    

@extend_schema(tags=['Igridients (only admin, storekeeper and superadmin can create, other restaurant-staff can only read)'])
class IngredientListCreateView(generics.ListCreateAPIView):
    serializer_class=IngredientSerializer
    permission_classes=[PermissionIngredient,IsAuthenticated]
   
    def get_queryset(self):
        user = self.request.user
                                        
        if user.is_superuser:
            return Ingredient.objects.all()
       
        if hasattr(user, 'restaurant') and user.restaurant:
                return Ingredient.objects.filter(restaurant=user.restaurant)
        return Ingredient.objects.none()   
    
    # def perform_create(self, serializer):
    #     restaurant_pk = self.kwargs.get('pk')
    #     serializer.save(restaurant_id=restaurant_pk)

    def perform_create(self, serializer):
            user = self.request.user

            if user.is_superuser:
                restaurant_pk = self.kwargs.get('pk')
                if restaurant_pk:
                    serializer.save(restaurant_id=restaurant_pk)
                else:
                    serializer.save()

            elif hasattr(user, 'restaurant') and user.restaurant:
                serializer.save(restaurant=user.restaurant)

            else:
                raise PermissionDenied(
                    'Siz esh qaysi restoranga biriktirilmegensiz!'
                )



@extend_schema(tags=['Igridients (only admin, storekeeper and superadmin can add, others only read)'])
class IngredientAddView(generics.UpdateAPIView):
    serializer_class = StockTransactionCreateSerializer
    permission_classes = [PermissionIngredient,IsAuthenticated]
   
    def get_queryset(self):
        user = self.request.user
                                        
        if hasattr(user, 'restaurant') and user.restaurant:
            return Ingredient.objects.filter(restaurant=user.restaurant)
       
        return Ingredient.objects.none()   
    
    @transaction.atomic  
    def perform_update(self, serializer):
        ingredient = self.get_object()
        stock_transaction = serializer.save(ingredient=ingredient)

        if stock_transaction.type == 'kirim':
            ingredient.current_stock += stock_transaction.quantity
        elif stock_transaction.type == 'shigim':
            ingredient.current_stock -= stock_transaction.quantity

        ingredient.save()
    
    
    
@extend_schema(tags=['Tables (only admin, waiter and superadmin can create, others only read)'])    
class TableListCreateView(generics.ListCreateAPIView, generics.UpdateAPIView):
    serializer_class=TableSerializer
    permission_classes=[PermissionTable, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
                                        
        if user.is_superuser:
            return Table.objects.all()
        if hasattr(user, 'restaurant') and user.restaurant:
            return Table.objects.filter(restaurant=user.restaurant)
        
        if Client.objects.filter(user=user).exists():
            return Table.objects.filter(status_is_free=True)
                
        return Table.objects.none()

    # def perform_create(self, serializer):
    #     restaurant_pk = self.kwargs.get('pk')
    #     serializer.save(restaurant_id=restaurant_pk)

    def perform_create(self, serializer):
            user = self.request.user

            if user.is_superuser:
                restaurant_pk = self.kwargs.get('pk')
                if restaurant_pk:
                    serializer.save(restaurant_id=restaurant_pk)
                else:
                    serializer.save()

            elif hasattr(user, 'restaurant') and user.restaurant:
                serializer.save(restaurant=user.restaurant)

            else:
                raise PermissionDenied(
                    'Siz esh qaysi restoranga biriktirilmegensiz!'
                )


       

@extend_schema(tags=['Orders (only admin, waiter and superadmin can create, others only read)'])   
class OrderListCreateView (generics.ListCreateAPIView): 
    serializer_class=OrderSerializer
    permission_classes=[PermissionOrder,IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
                                        
        if user.is_superuser:
            return Order.objects.all()
        if hasattr(user, 'restaurant') and user.restaurant:
            return Order.objects.filter(table__restaurant=user.restaurant)
        
        if Client.objects.filter(user=user).exists():
            return Order.objects.filter(client__user=user)
        return Order.objects.none()   

    # def perform_create(self, serializer):
    #     restaurant_pk = self.kwargs.get('pk')
    #     serializer.save(restaurant_id=restaurant_pk)

    # def perform_create(self, serializer):
    #         user = self.request.user

    #         if user.is_superuser:
    #             restaurant_pk = self.kwargs.get('pk')
    #             if restaurant_pk:
    #                 serializer.save(restaurant_id=restaurant_pk)
    #             else:
    #                 serializer.save()

    #         elif hasattr(user, 'restaurant') and user.restaurant:
    #             serializer.save(restaurant=user.restaurant)

    #         else:
    #             raise PermissionDenied(
    #                 'Siz esh qaysi restoranga biriktirilmegensiz!'
    #             )

        
        
@extend_schema(tags=['Active order items (only admin, chef and superadmin can update, others only read)'])       
class ActiveOrderItemView(generics.ListAPIView, generics.UpdateAPIView):
    serializer_class=OrderItemSerializer
    permission_classes=[PermissionActiveOrderItem, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user                   
        if user.is_superuser:
            return OrderItem.objects.filter(status='active')
        if hasattr(user, 'restaurant') and user.restaurant:
            if user.role in ['chef', 'admin']:
                return OrderItem.objects.filter(order__table__restaurant=user.restaurant, status='active')
            if user.role=='waiter':
                return OrderItem.objects.filter(order__table__restaurant=user.restaurant, order__waiter=user.id, status='active')
        return OrderItem.objects.none()  
    


@extend_schema(tags=['Order status (only admin, superadmin can update, others only read)'])   
class ChangeOrdersStatusView(generics.UpdateAPIView):
    serializer_class=StatusOrderSerializer
    permission_classes=[IsAuthenticated, PermissionChangeOrderStatus]

    def get_queryset(self):
        user = self.request.user         
        if user.is_superuser:
            return Order.objects.filter(status='active')
        if hasattr(user, 'restaurant') and user.restaurant:
            return Order.objects.filter(table__restaurant=user.restaurant, status='active')
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
    queryset=OrderItem.objects.all()
    serializer_class=OrderItemSerializer
    permission_classes=[IsAuthenticated, PermissionOrder]
    
    def get_queryset(self):
        user = self.request.user
        order_pk = self.kwargs.get('order_pk')
        #restaurant_id = self.kwargs.get('pk')

        if user.is_superuser:
            return OrderItem.objects.all()
        if hasattr(user, 'restaurant') and user.restaurant:
            return OrderItem.objects.filter(order=order_pk)
                
        if Client.objects.filter(user=user).exists():
            return OrderItem.objects.filter(order__client__user=user)
        return OrderItem.objects.none()  
    
    def perform_create(self, serializer):
        
        order_id = self.kwargs.get('order_pk')
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise NotFound("Заказ не найден")
            
        serializer.save(order=order)
    
    
    # def perform_create(self, serializer):
    #         user = self.request.user

    #         if user.is_superuser:
    #             restaurant_pk = self.kwargs.get('pk')
    #             if restaurant_pk:
    #                 serializer.save(restaurant_id=restaurant_pk)
    #             else:
    #                 serializer.save()

    #         elif hasattr(user, 'restaurant') and user.restaurant:
    #             serializer.save(restaurant=user.restaurant)

    #         else:
    #             raise PermissionDenied(
    #                 'Siz esh qaysi restoranga biriktirilmegensiz!'
    #             ) 
        




@extend_schema(tags=['RecipeItem (only admin, superadmin, storekeeper can create, others only read)'])   
class RecipeItemViewSet(generics.ListCreateAPIView):
    serializer_class = RecipeItemSerializer
    permission_classes = [IsAuthenticated, PermissionRecipe]

    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'restaurant') and user.restaurant:
            return RecipeItem.objects.filter(dish__restaurant=user.restaurant)

        restaurant_pk = self.kwargs.get('pk')
        if restaurant_pk:
            return RecipeItem.objects.filter(dish__restaurant_id=restaurant_pk)

        return RecipeItem.objects.none()

    def perform_create(self, serializer):
        dish = serializer.validated_data.get('dish')
        ingredient = serializer.validated_data.get('ingredient')
        if dish.restaurant != ingredient.restaurant:
            raise ValidationError("Dish penen inridient bir restoranga tiyisli boliw kerek!")

        serializer.save()


    
@extend_schema(tags=['RecipeItem (only admin, superadmin, storekeeper can update, others only read)']) 
class RecipeItemViewSet(generics.RetrieveUpdateAPIView):
    serializer_class = RecipeItemSerializer
    permission_classes = [IsAuthenticated, PermissionRecipe]

    def get_queryset(self):
        user = self.request.user
        restaurant_pk = self.kwargs.get('pk')
        # item_id = self.kwargs.get('id')
        

        if user.is_superuser or user.role in ['admin', 'storekeeper']:
            return RecipeItem.objects.filter(dish__restaurant_id=restaurant_pk)

        if hasattr(user, 'restaurant') and user.restaurant:
            return RecipeItem.objects.filter(dish__restaurant=user.restaurant)

        if getattr(user, 'role', None) == 'client':
            return RecipeItem.objects.filter(dish__restaurant_id=restaurant_pk)

        return RecipeItem.objects.none() 
    

    
    
    
    
    
@extend_schema(tags=['Reservation (only admin, superadmin, clients can create, others only read)'])  
class ReservationListCreateView(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, PermissionReservation]

    def get_queryset(self):
        user = self.request.user
        restaurant_pk = self.kwargs.get('pk')

        if user.is_superuser:
            if restaurant_pk:
                return Reservation.objects.filter(restaurant_id=restaurant_pk)
            return Reservation.objects.all()

        if user.role == 'client':
            return Reservation.objects.filter(client=user.client)

        if user.role == 'admin':
            if user.restaurant:
                return Reservation.objects.filter(restaurant=user.restaurant)
            return Reservation.objects.none()

        return Reservation.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        restaurant_pk = self.kwargs.get('pk')

        if user.role == 'client':
            client = user.client
            if not restaurant_pk:
                raise serializers.ValidationError({"restaurant": "ID restoran URL da korsetilmegen."})
            serializer.save(restaurant_id=restaurant_pk, client=client)

        elif user.role == 'admin':
            if not user.restaurant:
                raise serializers.ValidationError({"detail": "Bul admin restoranga biriktirilmegen."})
            serializer.save(restaurant=user.restaurant)

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
    
    




@extend_schema(tags=['ClientList']) 
class ClientListView(generics.ListAPIView):
    queryset=Client.objects.all()
    serializer_class=ClientSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
            user1 = self.request.user
            if user1.is_superuser:
                return Client.objects.filter(user__role='client')
            
            if user1.restaurant:
                 return Client.objects.filter(user__restaurant=user1.restaurant).distinct()
            
            if Client.objects.filter(user=user1).exists():
                return Client.objects.filter(user=user1)
                
            return Client.objects.none() 
        
        
    # def perform_create(self, serializer):
    #     restaurant_pk = self.kwargs.get('pk')
    #     serializer.save(restaurant_id=restaurant_pk)




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

