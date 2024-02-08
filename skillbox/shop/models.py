from django.contrib.auth.models import User
from django.db import models
import random
import string
from datetime import datetime

#Категории
class Category(models.Model):
    """
    Category - модель в которой храняться группы товаров (категория, вид товара).
    Определив группа, далле в Продуктах при создании товару можно присвоить его группу
    """
    name = models.CharField("Название категории",max_length=50)

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product - модель для хранения данных о товаре
    """
    sku = models.CharField("Артикул",max_length=10, unique=True, editable=False)
    name = models.CharField("Имя товара",max_length=100)
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField("Количество",)
    price = models.DecimalField("Цена",max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ["name", "price"]
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        
    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_sku()
        super(Product, self).save(*args, **kwargs)

    def generate_sku(self):
        letters = string.ascii_uppercase
        digits = string.digits
        random_letters = ''.join(random.choices(letters, k=3))
        random_digits = ''.join(random.choices(digits, k=3))
        return f'{random_letters}-{random_digits}'
    
# Заказы
class Order(models.Model):
    """
    Order - модель для хранения данных о заказе
    """
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    status = models.BooleanField("Статус заказа", default=False, editable=False)
    products = models.ManyToManyField(Product, through='OrderItem')
    
    class Meta:
        ordering = ["user",]
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return 'Заказ'
    
    
#Tabular      
class OrderItem(models.Model):
    """
    OrderItem - промежуточную модель между Order и Product, 
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE,  related_name='items')
    product = models.ForeignKey(Product, verbose_name="Продукт", on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Количество", default=1)

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.product} - {self.quantity}'
    
# Для отчета
class PurchaseReport(models.Model):
    """
    PurchaseReport - эта модель предназначена для хранения отчетов о покупках,
    создаваемых для пользователей.
    """
    user = models.CharField("Пользователь", max_length=100)
    products = models.TextField("Список продуктов и количество")
    purchase_date = models.DateTimeField("Дата покупки", default=datetime.now)
    
    class Meta:
        verbose_name = 'Отчет по покупкам'
        verbose_name_plural = 'Отчеты по покупкам'