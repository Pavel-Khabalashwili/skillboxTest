from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe
import csv

from django.http import HttpResponse
from django.utils.encoding import smart_str


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display =  "name", 
    list_display_links = "name", 
    ordering = "name",
    search_fields = "name", 
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display =  "sku", "name", "category", "quantity", "price"
    list_display_links = "sku", "name",
    ordering = "name", "id",
    search_fields = "sku", "name", "category",
    

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    
    readonly_fields = ['product_info']
    def product_info(self, obj):
        return f'{obj.product.name} - {obj.quantity}'
    product_info.short_description = 'Продукт и количество'
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = 'user_name',"get_order_items",'status',
    list_display_links = 'user_name','status'
    ordering = 'user__username',
    search_fields = 'user__username',

    def user_name(self, obj):
        return obj.user.get_full_name() if obj.user.get_full_name() else obj.user.username
    user_name.short_description = 'Пользователь'
    
    def get_order_items(self, obj):
        items = obj.items.all()
        return ', '.join([f'{item.product.name} - {item.quantity}' for item in items])
    get_order_items.short_description = 'Список продуктов и количеств'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user')
        return queryset.prefetch_related('items__product')
    
    # def product_info(self, obj):
    #     products = obj.products.all()
    #     return ', '.join([f'{product.name}' for product in products])
    # product_info.short_description = 'Продукты'

@admin.register(PurchaseReport)
class PurchaseReportAdmin(admin.ModelAdmin):
    list_display = 'user', 'products', 'purchase_date'
    list_filter = ('purchase_date',)
    actions = ['export_as_csv', 'export_as_html']

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="purchase_report.csv"'

        writer = csv.writer(response)
        writer.writerow([smart_str('User'), smart_str('Products'), smart_str('Purchase Date')])

        for report in queryset:
            writer.writerow([smart_str(report.user), smart_str(report.products), smart_str(report.purchase_date)])

        return response
    
    export_as_csv.short_description = "Скачать СSV файл"
    
    def export_as_html(self, request, queryset):
        html_content = '<html><head><title>Purchase Report</title></head><body><table>'
        html_content += '<tr><th>User</th><th>Products</th><th>Purchase Date</th></tr>'
        
        for report in queryset:
            html_content += f'<tr><td>{report.user}</td><td>{report.products}</td><td>{report.purchase_date}</td></tr>'
        
        html_content += '</table></body></html>'

        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="purchase_report.html"'
        
        with open('purchase_report.html', 'w') as file:
            file.write(html_content)

        return response

    export_as_html.short_description = "Скачать HTML файл"