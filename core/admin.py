from django.urls import path
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.utils.timezone import now
from .models import Sale
from decimal import Decimal
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.utils.html import format_html
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


class AdminTotalSalesView(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('total-sales/', self.admin_site.admin_view(self.total_sales_view), name='total-sales'),
        ]
        return my_urls + urls

    def total_sales_view(self, request):
        if not request.user.is_superuser:
            self.message_user(request, "You do not have permission to view this.", level=messages.ERROR)
            return redirect('/admin/')

        today = now().date()
        todays_sales = Sale.objects.filter(date__date=today)

        gross_total = sum(s.total for s in todays_sales)
        # Placeholder discount/tax logic (update this if needed)
        discount = Decimal('0.05')  # 5%
        tax = Decimal('0.12')       # 12%
        discounted_total = gross_total * (1 - discount)
        net_total = discounted_total * (1 + tax)

        if 'reset' in request.GET:
            count = todays_sales.count()
            todays_sales.delete()
            self.message_user(request, f"Reset successful. {count} sales deleted.")
            return redirect('admin:total-sales')

        context = dict(
            self.admin_site.each_context(request),
            gross_total=gross_total,
            discounted_total=discounted_total,
            net_total=net_total,
            sales=todays_sales,
            title='Total Sales Dashboard',
        )
        return render(request, 'admin/total_sales.html', context)


@staff_member_required
def total_sales_admin_view(request):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to view this.")
        return redirect("/admin/")

    today = now().date()
    todays_sales = Sale.objects.filter(date__date=today)

    gross_total = sum(s.total for s in todays_sales)
    discount = Decimal('0.05')
    tax = Decimal('0.12')
    discounted_total = gross_total * (1 - discount)
    net_total = discounted_total * (1 + tax)

    if 'reset' in request.GET:
        count = todays_sales.count()
        todays_sales.delete()
        messages.success(request, f"{count} sales deleted for today.")
        return redirect('admin:total-sales')

    context = {
        'title': "Total Sales Today",
        'gross_total': gross_total,
        'discounted_total': discounted_total,
        'net_total': net_total,
        'sales': todays_sales,
    }
    return render(request, 'admin/total_sales.html', context)

# ✅ Add this at the bottom of your admin.py

# Dummy model to show "📊 Total Sales" in the sidebar
from django.db import models

class TotalSalesDummy(models.Model):
    class Meta:
        verbose_name_plural = '📊 Total Sales'
        app_label = 'core'
        managed = False  # no DB table created

# Admin for the dummy model, redirecting to the custom view
class TotalSalesAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('admin:total-sales')

# Register the dummy model in the sidebar
admin.site.register(TotalSalesDummy, TotalSalesAdmin)

# Route the custom admin view manually
from django.contrib.admin.sites import AdminSite

original_get_urls = admin.site.get_urls

def custom_admin_urls():
    def wrap(view):
        return admin.site.admin_view(view)

    custom_urls = [
        path('core/total-sales/', wrap(total_sales_admin_view), name='total-sales'),
    ]
    return custom_urls + original_get_urls()

admin.site.get_urls = custom_admin_urls
