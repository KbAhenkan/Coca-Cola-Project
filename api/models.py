from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Customer', 'Customer'),
        ('Admin', 'Admin')
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Customer')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True) # Had to make this temporarily nullable because I had already created some Products in the database 

    def __str__(self):
        return self.name



class Order(models.Model):
    STATUS = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ] 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')

    def __str__(self):
        return f'Order #{self.id} by {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} {self.product} for {self.price_at_purchase}'

