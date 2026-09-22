from rest_framework import permissions
from .models import Client

class PermissionRestaurat(permissions.BasePermission):
    def has_permission(self, request, view):
        # Все запросы требуют авторизации
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if request.method in ['POST','DELETE','PATCH','PUT']:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False



class PermissionUser(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.role == 'admin':
            return True

        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True

        if user.role == 'admin':
            if hasattr(user, 'restaurant') and user.restaurant:
                return obj.restaurant == user.restaurant
        
        if request.method in permissions.SAFE_METHODS:
            return obj == user
        return False
    
    
    
    
class PermissionCategory(PermissionUser):
    pass


class PermissionDish(PermissionUser):
    pass




class PermissionDishStatus(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.role in ['admin', 'waiter', 'chef', 'storekeeper']:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False
    
class PermissionIngredient(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.role in ['admin', 'storekeeper']:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False


class PermissionTable(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.role in ['admin', 'waiter']:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False
    

class PermissionOrder(PermissionTable):
    pass


class PermissionActiveOrderItem(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.role in ['admin', 'chef']:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False
    


class PermissionChangeOrderStatus(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.role in ['admin']:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False
    

class PermissionRecipe(PermissionChangeOrderStatus):
    def has_object_permission(self, request, view, obj):
    
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        if request.user.role in ['admin', 'storekeeper']:
            if hasattr(request.user, 'restaurant') and request.user.restaurant:
                return obj.dish.restaurant == request.user.restaurant
        return False

    
      
class PermissionReservation(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.role in ['admin', 'client']:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return False
    
    
class PermissionReservationForClient(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role =='client':
            return True

        return False
 
    
    

