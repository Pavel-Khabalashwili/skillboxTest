from django.urls import reverse
from .models import Product,Order, OrderItem, Category, PurchaseReport
from django.contrib.auth.models import User
from unittest.mock import patch
from django.test import TestCase, Client


#200 и redirect       
class ShopViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='test_user')
        self.product = Product.objects.create(name='Test Product', category=Category.objects.create(name='Test Category'), quantity=10, price=100)

    def test_products_list_view(self):
        response = self.client.get(reverse('shop:products-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/products-list.html')

    def test_product_detail_view(self):
        response = self.client.get(reverse('shop:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product-detail.html')

    def test_order_detail_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('shop:order-detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order-detail.html')

    def test_buy_product_view(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('shop:buy-product'))
        self.assertEqual(response.status_code, 302)  # Redirects to products list after purchase

    def test_upload_product_csv_view(self):
        self.client.force_login(self.user)
        with open('test_products.csv', 'w') as file:
            # Write some test CSV data
            pass
        with open('test_products.csv', 'rb') as file:
            response = self.client.post(reverse('shop:import'), {'file': file})
            self.assertEqual(response.status_code, 302)  # Redirects after successful import

    def tearDown(self):
        User.objects.all().delete()
        Product.objects.all().delete()
        Order.objects.all().delete()
        OrderItem.objects.all().delete()
        PurchaseReport.objects.all().delete()
        Category.objects.all().delete()
    
# Проверка данных
class ProductsListViewTest(TestCase):
    def test_products_list_view(self):
        response = self.client.get(reverse('shop:products-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/products-list.html')
        products = response.context['products']
        self.assertTrue(all(isinstance(product, Product) for product in products))

#Ответ    
class ProductDetailViewTest(TestCase):
    def test_get_request(self):
        cat = Category.objects.create(name = "lll")
        product = Product.objects.create(name='Test Product', quantity=10, price = 10, category = cat, sku = "XYZ-456")
        response = self.client.get(reverse('shop:product-detail', kwargs={'pk': product.pk}))
        self.assertEqual(response.status_code, 200)

#Статус, данные
class OrderDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.order = Order.objects.create(user=self.user)
        category = Category.objects.create(name='Test Category') 
        self.product = Product.objects.create(name='Test Product', price=10, quantity=1, category=category)  
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1)

    def test_order_detail_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('shop:order-detail'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order-detail.html')
        self.assertEqual(response.context['order'], self.order)
        self.assertEqual(list(response.context['order_items']), [self.order_item])
        
class BuyProductViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        category = Category.objects.create(name='Test Category')  
        self.product = Product.objects.create(name='Test Product', quantity=10, price=100, category=category)
        self.order = Order.objects.create(user=self.user)

    def test_buy_product_view(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('shop:buy-product'))
        self.assertEqual(response.status_code, 302)  
        self.order.refresh_from_db()
        self.assertTrue(self.order.status)  
        self.assertEqual(Product.objects.get(id=self.product.id).quantity, 9)

    