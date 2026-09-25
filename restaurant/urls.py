
from django.urls import path
from .views import  LogoutView ,ClientRegisterView, OrderItemViewSet, RecipeItemUpdateViewSet, CustomTokenObtainPairView, RestaurantListCreateView, RestaurantRetrieveUpdateDestroyView, ChangeOrdersStatusView, UserListCreateView, UserRetrieveUpdateDestroyView, ClientListView, CategoryListCreateView, DishListCreateView, DishStatusChangeView, IngredientListCreateView, IngredientAddView, RecipeItemViewSet, TableListCreateView,TableDetailView, OrderListCreateView, ActiveOrderItemListView,ActiveOrderItemUpdateView, ReservationListCreateView, ReservationListForClientView, ClientDetailPageView
from rest_framework_simplejwt.views import (
        TokenRefreshView
)



urlpatterns = [
    path('api/auth/register/', ClientRegisterView.as_view(), name='client-register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    
    
    path('restaurants/', RestaurantListCreateView.as_view(), name='restaurant-list-create'),
    path('restaurants/<int:pk>/', RestaurantRetrieveUpdateDestroyView.as_view(), name='restaurant-detail'),
    path('restaurants/<int:pk>/staff/', UserListCreateView.as_view(), name='user-list-create' ),
    path('staff/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail' ),
    path('restaurants/<int:pk>/categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('restaurants/<int:pk>/dishes/', DishListCreateView.as_view(), name='dish-list-create'),
    path('dishes/<int:pk>/toggle-availability/', DishStatusChangeView.as_view(), name='dish-availability'),
    
    path('restaurants/<int:pk>/tables/', TableListCreateView.as_view(), name='dish-list-create'),
    path('restaurants/<int:restaurant_pk>/tables/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
    
    path('restaurants/<int:pk>/orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('restaurants/<int:pk>/orders/<int:order_pk>/items/', OrderItemViewSet.as_view(), name='order-items'),
    path('kitchen/orders/', ActiveOrderItemListView.as_view(), name='active-order-list'),
    path('kitchen/orders/<int:pk>/', ActiveOrderItemUpdateView.as_view(), name='active-order-update'),
    path('orders/<int:pk>/status/', ChangeOrdersStatusView.as_view(), name='change-order-status'),
    path('restaurants/<int:pk>/ingredients/', IngredientListCreateView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:pk>/stock-in/', IngredientAddView.as_view(), name='ingredient-add'),
    path('restaurants/<int:pk>/recipeitem/', RecipeItemViewSet.as_view(), name='recipeitem-list-create'),
    path('restaurants/<int:pk>/recipeitem/<int:item_pk>/', RecipeItemUpdateViewSet.as_view(), name='recipeitem-detail-update'),

    path('restaurants/<int:pk>/reservations/', ReservationListCreateView.as_view(), name='reservation-list-create'),
    path('my-reservations/', ReservationListForClientView.as_view(), name='client-reservation-list'),
    path('restaurants/<int:pk>/clients/', ClientListView.as_view(), name='client-list'),
    path('me/', ClientDetailPageView.as_view(), name='client-personal-page')
    
]