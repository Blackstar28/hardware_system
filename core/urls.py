from django.urls import path
from . import views
from .views import DeliveryListView, mark_delivery_received, undo_delivery

urlpatterns = [
    path('', views.home_view, name='home'),
    path('pos/', views.pos_view, name='pos_view'),
    path("pos/", views.pos_sale, name="pos_sale"),
    path('receipt/<int:sale_id>/pdf/', views.generate_receipt_pdf, name='generate_receipt_pdf'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/new/', views.create_purchase_order, name='create_purchase_order'),
    path('ajax/get-product-price/', views.get_product_price, name='get_product_price'),
    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('deliveries/mark/<int:pk>/', mark_delivery_received, name='mark_delivery'),
    path('deliveries/undo/<int:pk>/', undo_delivery, name='undo_delivery'),
    path('deliveries/<int:pk>/toggle/', views.toggle_delivery_status, name='mark_as_delivered'),
    path('test-telegram/', views.test_telegram, name='test_telegram'),
    path('admin/core/total-sales/', views.dashboard_view, name='dashboard_view'),
    path('admin/core/total-sales/pdf/', views.download_sales_pdf, name='download_sales_pdf'),
    path('admin/core/total-sales/archive/', views.archived_sales_view, name='archived_sales_view'),
    
]
