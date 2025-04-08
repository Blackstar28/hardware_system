from django.contrib import admin
from .models import (
    Product, Sale, SaleItem,
    Supplier, PurchaseOrder, PurchaseOrderItem,
    Delivery, DeliveryItem
)

# Register simple models
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SaleItem)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email')
    search_fields = ('name',)

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'date_created', 'status')
    list_filter = ('status',)
    inlines = [PurchaseOrderItemInline]

class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 1

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'purchase_order', 'delivery_date', 'received_by')
    list_filter = ('delivery_date',)
    inlines = [DeliveryItemInline]
