from django.db import models
from django.contrib.auth.models import AbstractUser



class Restaurant(models.Model):
    name=models.CharField(max_length=50, unique=True, null=False, blank=False, verbose_name='restoran_ati')
    address=models.CharField(max_length=100,null=False, blank=False, verbose_name='restoran_adresi')
    phone=models.CharField(max_length=12, null=False, blank=False, verbose_name='restoran_tel_nomeri')
    
    logo = models.ImageField(upload_to='restaurants/logos/', null=True, blank=True, verbose_name='restoran_logosi')
    is_active=models.BooleanField(default=True, null=False, blank=False, verbose_name='restoran_statusi')
    def __str__(self):
            return self.name



class User(AbstractUser):
    phone=models.CharField(max_length=12, null=False, blank=False, verbose_name='user_tel_nomeri')
    role=models.CharField(max_length=20, null=False, blank=False, verbose_name='user_roli')
    restaurant=models.ForeignKey(Restaurant, null=True, blank=True, on_delete=models.CASCADE, verbose_name='restoran', related_name='user')
    
    def __str__(self):
            return self.username
        
        
        
class Client(models.Model):
    
    user=models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='klient', related_name='client')
    
    def __str__(self):
            return self.user.username
        
        
class Category(models.Model):   
    name=models.CharField(max_length=50, unique=True, null=False, blank=False, verbose_name='kategoriya_ati')
    order_index=models.CharField(max_length=50, unique=True, null=False, blank=False, verbose_name='kategoriya_indeksi')
    
    restaurant=models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='restoran', related_name='categories')
    
    def __str__(self):
            return self.name

class Dish(models.Model):
    name=models.CharField(max_length=50, unique=True, null=False, blank=False, verbose_name='zakaz_ati')
    description=models.CharField(max_length=200, unique=False, null=False, blank=False, verbose_name='qosimsha')
    price=models.IntegerField(null=False, blank=False, verbose_name='awqat/ishimlik bahasi')
    logo = models.ImageField(upload_to='dishes/logos/', null=True, blank=True, verbose_name='zakaz_logosi')
    is_available=models.BooleanField(default=True, null=False, blank=False, verbose_name='zakaz_bar_elenligi')
    
    restaurant=models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='restoran', related_name='dishes')
    category=models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='categoriya', related_name='dishes')
    
    def __str__(self):
            return self.name
        

class Ingredient(models.Model):
    name=models.CharField(max_length=50, unique=True, null=False, blank=False, verbose_name='ingidient_ati')
    unit=models.CharField(max_length=50, unique=False, null=False, blank=False, verbose_name='ingridient_olshemi')
    current_stock=models.IntegerField(null=False, blank=False, verbose_name='skladtagi_qaldiq')
    restaurant=models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='restoran', related_name='ingredient')
    
    def __str__(self):
            return self.name
        

class RecipeItem(models.Model):
    
    quantity_per_serving=models.IntegerField(null=False, blank=False)
    dish=models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name='dish', related_name='recipeitem')
    ingredient=models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='maxsulat', related_name='recipeitem')
    


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('kirim', 'Kirim'),
        ('shigim', 'Shigim'),
    ]

    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, null=False, blank=False, verbose_name='tranzaksiya_turi')
    quantity = models.IntegerField(null=False, blank=False, verbose_name='mugdari')
    reason = models.CharField(max_length=255, null=True, blank=True, verbose_name='sebebi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='tranzaksiya_waqti')
    
    ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='ingridient', related_name='transactions')

    def __str__(self):
        return f"{self.get_type_display()} - {self.ingredient.name}: {self.quantity}"



class Table(models.Model):
    number=models.IntegerField(null=False, blank=False)
    seats_count=models.IntegerField(null=False, blank=False)
    status_is_free=models.BooleanField(null=False, blank=False, verbose_name='stol_statusi')
    
    restaurant=models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='restoran', related_name='table')


class Order(models.Model):
    status=models.CharField(max_length=20, null=False, blank=False, verbose_name='zakaz_statusi')
    payment_method=models.CharField(max_length=20, null=False, blank=False, verbose_name='tolem_turi')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='jaratilgan_waqti')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='jawilgan_waqti')
    
    table=models.ForeignKey(Table, on_delete=models.CASCADE,  verbose_name='stol', related_name='order')
    waiter=models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ofitsiant', related_name='order')
    client=models.ForeignKey(Client, null=True, blank=True, on_delete=models.CASCADE, verbose_name='klient', related_name="order")
    
    def __str__(self):
            return f"Order #{self.id} - {self.status}"

class OrderItem(models.Model):
    quantity=models.IntegerField(null=False, blank=False)
    note=models.CharField(max_length=50, blank=True, null=True,  verbose_name='zakazga_itemga_qosimsha')
    status=models.CharField(max_length=50,  verbose_name='zakaz_item_statusi')
    
    dish=models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name='awqat/ishimlik', related_name='order_item')
    order=models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='zakaz', related_name='order_item')
    
    
    
    
class Reservation(models.Model):
    datetime = models.DateTimeField(verbose_name='rezerv_waqti')
    guests_count=models.IntegerField(null=False, blank=False)
    status=models.CharField(max_length=50,  verbose_name='rezerv_statusi')
    
    
    
    client=models.ForeignKey(Client, null=True, blank=True,  on_delete=models.CASCADE,  verbose_name='rezerv qilgan klient', related_name='reservation')
    restaurant=models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name='rezerv qilingan restoran', related_name='reservation')
    table=models.ForeignKey(Table, on_delete=models.CASCADE,  verbose_name='rezerv qilingan stol', related_name='reservation')
    
    def __str__(self):
        return f"Reservation #{self.id} - {self.client} ({self.datetime})"