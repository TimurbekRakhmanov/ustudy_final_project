from django.contrib import admin
from .models import Restaurant, User, Category, Ingredient, Dish, RecipeItem, Table, Order, OrderItem, Reservation
# Register your models here.
from django.contrib.auth.admin import UserAdmin


admin.site.register(Category)
admin.site.register(Dish)
admin.site.register(Ingredient)
admin.site.register(RecipeItem)
admin.site.register(Table)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Reservation)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active', 'phone')
    list_filter = ('is_active', 'name', 'phone')
    search_fields = ('name', 'phone')
    
@admin.register(User)
class UserAdmin(UserAdmin):
    # Добавляем кастомные поля в интерфейс редактирования пользователя в админке
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'role', 'restaurant')}),
    )
    # И в форму создания нового пользователя
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'role', 'restaurant')}),
    )


