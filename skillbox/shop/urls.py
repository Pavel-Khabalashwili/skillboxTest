from django.urls import path,  include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = "shop"

routers = DefaultRouter()
routers.register("products", ProductViewSet)

urlpatterns = [
    path("api/", include(routers.urls)),
    path("", ProductsListView.as_view(), name="products-list"),
    path("shop/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("shop/order/", OrderDetailView.as_view(), name="order-detail"),
    path("buy-product/", BuyProductView.as_view(), name="buy-product"),
    path("import/", upload_product_csv, name="import"),
]
