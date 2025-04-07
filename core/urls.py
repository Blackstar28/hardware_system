from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('pos/', views.pos_view, name='pos_view'),
    path('receipt/<int:sale_id>/pdf/', views.generate_receipt_pdf, name='generate_receipt_pdf'),
]
