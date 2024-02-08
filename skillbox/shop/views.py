from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, RedirectView, TemplateView
from django.contrib import messages
from .models import Product, Order, OrderItem, PurchaseReport, Category
from django.http import HttpResponseRedirect, HttpResponse
from .forms import ProductUploadForm
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ProductSerializers
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
import csv
import chardet


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['name']
    filterset_fields = ['name', 'price', 'category', 'quantity']
    ordering_fields = ['name', 'price', 'category']
    
class ProductsListView(ListView):
    model = Product
    template_name = "shop/products-list.html"
    context_object_name = "products"
    
class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product-detail.html"
    context_object_name = "product"

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        quantity = int(request.POST.get('quantity', 1))
        user = request.user
        order = Order.objects.filter(user=user).first()

        if order is None:
            order = Order.objects.create(user=user)

        order_item = order.items.filter(product=product).first()
        
        if order_item:
            if product.quantity >= order_item.quantity + quantity:
                order_item.quantity += quantity
            else:
                order_item.quantity = product.quantity
            order_item.save()
        else:
            if product.quantity >= quantity:
                OrderItem.objects.create(order=order, product=product, quantity=quantity)
            else:
                OrderItem.objects.create(order=order, product=product, quantity=product.quantity)

        success_url = reverse('shop:products-list')
        return HttpResponseRedirect(success_url)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'shop/order-detail.html'
    context_object_name = 'order'
    login_url = reverse_lazy('authentication:authentication')

    def get_object(self):
        user = self.request.user
        return Order.objects.filter(user=user).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        if order:
            order_items = order.items.annotate(total_price=F('quantity') * F('product__price'))
            total_price_per_item = order_items.values('product__name').annotate(total=Sum('total_price'))
            total_price = sum(item['total'] for item in total_price_per_item)
            
            context['order_items'] = order_items
            context['total_price_per_item'] = total_price_per_item
            context['total_price'] = total_price
        else:
            context['order_items'] = []
            context['total_price_per_item'] = []
            context['total_price'] = 0

        return context
    
class BuyProductView(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'shop:products-list'  
    def post(self, request):
        order = Order.objects.filter(user=request.user, status=False).first()
        if order:
            purchase_data = {
                'user': order.user.get_full_name() if order.user.get_full_name() else order.user.username,
                'products': ', '.join([f'{item.product.name} - {item.quantity}' for item in order.items.all()])
            }
            PurchaseReport.objects.create(**purchase_data)
            for item in order.items.all():
                product = item.product
                product.quantity -= item.quantity
                product.save()
            order.status = True
            order.save()
            order.items.all().delete()  
            order.delete()
            messages.success(request, 'Заказ успешно приобритен.')
        return super().get(request)
    
def upload_product_csv(request):
    if request.method == 'POST':
        form = ProductUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            
            raw_data = csv_file.read()
            result = chardet.detect(raw_data)
            csv_file.seek(0)
            encoding = result['encoding']
            
            decoded_file = raw_data.decode(encoding).splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                category_name = row['Категория']
                print(f"Category name extracted: {category_name}")  
                
                if category_name == None:
                    return redirect('shop:products-list')
                try:
                    category = Category.objects.get(name=category_name)
                except Category.DoesNotExist:
                    category = Category.objects.create(name=category_name)

                Product.objects.create(
                    name=row['Название'],
                    category=category,
                    quantity=int(row['Количество']),
                    price=float(row['Цена'])
                )
            
            return redirect(reverse('shop:products_list'))
    else:
        form = ProductUploadForm()
    return render(request, 'shop/import-csv.html', {'form': form})
