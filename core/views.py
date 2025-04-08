from django.shortcuts import render, redirect
from . import models
from .models import Product, Sale, SaleItem
from .forms import POSFormSet
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit
from django.core.mail import send_mail
from core.utils import send_telegram_message
from django.db.models import F
from .models import PurchaseOrder, PurchaseOrderItem
from .forms import PurchaseOrderForm, POItemFormSet
from .forms import PurchaseOrderForm, PurchaseOrderItemFormSet
from django.db.models import Q
from django.views.generic import ListView
from .models import Delivery
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from core.utils import notify_low_stock
from django.contrib import messages
from core.models import Product
from django.conf import settings
from django.http import HttpResponse
import requests


def purchase_order_list(request):
    return render(request, 'core/purchase_order_list.html', {})

def pos_view(request):
    products = Product.objects.all()
    return render(request, 'pos.html', {'products': products})

def home_view(request):
    return render(request, 'core/home.html')

# Check if user is cashier
def is_cashier(user):
    return user.groups.filter(name='Cashier').exists() or user.is_superuser

# Generate PDF Receipt
# Generate PDF Receipt
def generate_receipt_pdf(request, sale_id):
    sale = Sale.objects.get(id=sale_id)
    items = SaleItem.objects.filter(sale=sale)

    # Build the receipt data with pre-calculated line totals
    receipt = []
    for item in items:
        receipt.append({
            'name': item.product.name,
            'quantity': item.quantity,
            'price': item.price,
            'line_total': item.quantity * item.price
        })

    path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    html = render_to_string("core/receipt_template.html", {
        'sale': sale,
        'items': receipt,
        'total': sale.total,
    })
    pdf = pdfkit.from_string(html, False, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_{sale.id}.pdf"'
    return response


# POS View
@user_passes_test(is_cashier)
@login_required
def pos_view(request):
    formset = POSFormSet(request.POST or None)

    if request.method == 'POST' and formset.is_valid():
        sale = Sale.objects.create(cashier=request.user, total=0)
        total = 0
        receipt = []

        for form in formset:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                product = form.cleaned_data['product']
                quantity = form.cleaned_data['quantity']

                if product.stock >= quantity:
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )
                    product.stock -= quantity
                    product.save()
                    notify_low_stock(product)

                    line_total = product.price * quantity
                    total += line_total
                    receipt.append({
                        'name': product.name,
                        'qty': quantity,
                        'unit': product.price,
                        'total': line_total
                    })
                else:
                    messages.error(request, f"Not enough stock for {product.name}")
                    sale.delete()
                    return redirect('pos_view')

        sale.total = total
        sale.save()

        # Option 1: Redirect to PDF directly
        # Show HTML receipt page with buttons
        return render(request, 'core/receipt.html', {
        'sale': sale,
        'receipt': receipt,
        'total': total,
})


        # Option 2 (if using receipt.html):
        # return render(request, 'core/receipt.html', {
        #     'sale': sale,
        #     'receipt': receipt,
        #     'total': total,
        # })

    return render(request, 'core/pos.html', {
        'formset': formset,
        'products': Product.objects.all(),
        'empty_form': formset.empty_form,
    })

def check_and_notify_low_stock():
    low_stock_products = Product.objects.filter(stock__lte=F('low_stock_threshold'))
    if low_stock_products.exists():
        product_list = "\n".join([f"{p.name} (Stock: {p.stock})" for p in low_stock_products])
        send_mail(
            subject='⚠️ Low Stock Alert',
            message=f'The following products are low on stock:\n\n{product_list}',
            from_email='ajkleinf@gmail.com',
            recipient_list=['ajkleinf@gmail.com'],
            fail_silently=False,
        )
    # After saving the sale and reducing stock
check_and_notify_low_stock()

def create_purchase_order(request):
    if request.method == 'POST':
        po_form = PurchaseOrderForm(request.POST)
        formset = POItemFormSet(request.POST)

        if po_form.is_valid() and formset.is_valid():
            po = po_form.save()
            po_items = formset.save(commit=False)
            for item in po_items:
                item.po = po
                item.save()
            formset.save_m2m()
            return redirect('purchase_order_list')  # Change to your actual success URL
    else:
        po_form = PurchaseOrderForm()
        formset = POItemFormSet()

    return render(request, 'purchase_orders/create_po.html', {
        'po_form': po_form,
        'formset': formset,
    })




def create_purchase_order(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = POItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            purchase_order = form.save()
            items = formset.save(commit=False)

            for item in items:
                item.purchase_order = purchase_order
                item.save()

            return redirect('purchase_order_success')  # You can change this
    else:
        form = PurchaseOrderForm()
        formset = POItemFormSet()

    return render(request, 'core/create_purchase_order.html', {
        'form': form,
        'formset': formset
    })

def create_purchase_order(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            po = form.save()
            items = formset.save(commit=False)
            for item in items:
                item.purchase_order = po
                item.save()
            return redirect('purchase_order_list')  # You can change this later
    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet(queryset=PurchaseOrderItem.objects.none())
    
    return render(request, 'core/create_purchase_order.html', {
        'form': form,
        'formset': formset
    })
def delivery_list_view(request):
    deliveries = Delivery.objects.all().order_by('-delivery_date')  # newest first
    return render(request, 'core/deliveries.html', {'deliveries': deliveries})

def delivery_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', 'delivery_date')

    deliveries = Delivery.objects.all()

    if search_query:
        deliveries = deliveries.filter(
            Q(purchase_order__supplier__name__icontains=search_query) |
            Q(purchase_order__id__icontains=search_query)
        )

    if status_filter == 'delivered':
        deliveries = deliveries.filter(delivered=True)
    elif status_filter == 'not_delivered':
        deliveries = deliveries.filter(delivered=False)

    if sort_by in ['delivery_date', '-delivery_date', 'delivered']:

        deliveries = deliveries.order_by(sort_by)

    # Optional: paginate (10 per page)
    paginator = Paginator(deliveries, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'deliveries': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by
    }
    return render(request, 'core/delivery_list.html', context)

class DeliveryListView(ListView):
    model = Delivery
    template_name = 'deliveries/delivery_list.html'
    context_object_name = 'deliveries'

    def get_queryset(self):
        queryset = Delivery.objects.select_related('purchase_order', 'purchase_order__supplier')

        search_query = self.request.GET.get('q', '')
        status_filter = self.request.GET.get('status', '')

        if search_query:
            queryset = queryset.filter(
                Q(purchase_order__supplier__name__icontains=search_query) |
                Q(purchase_order__id__icontains=search_query)
            )

        if status_filter == 'delivered':
            queryset = queryset.filter(received=True)
        elif status_filter == 'pending':
            queryset = queryset.filter(received=False)

        sort_by = self.request.GET.get('sort', 'date_received')
        if sort_by in ['date_received', '-date_received']:
            queryset = queryset.order_by(sort_by)

        return queryset
    
def mark_delivery_received(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    delivery.received = True
    delivery.save()
    messages.success(request, f'Delivery {delivery.pk} marked as received.')
    return redirect('delivery_list')

def undo_delivery(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    delivery.received = False
    delivery.save()
    messages.info(request, f'Delivery {delivery.pk} marked as pending.')
    return redirect('delivery_list')

def toggle_delivery_status(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    delivery.delivered = not delivery.delivered
    delivery.save()
    
    if delivery.delivered:
        messages.success(request, "Delivery marked as delivered.")
    else:
        messages.warning(request, "Delivery marked as *not* delivered.")
    
    return redirect('delivery_list')

def pos_sale(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id)

            if product.stock >= quantity:
                product.stock -= quantity
                product.save()

                # 🔔 Send alert if stock is low
                notify_low_stock(product)

                messages.success(request, f"{product.name} sold. Remaining stock: {product.stock}")
            else:
                messages.error(request, f"Not enough stock for {product.name}")
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")

        return redirect("pos_sale")  # reloads POS page

    products = Product.objects.all()
    return render(request, "pos.html", {"products": products})

def test_telegram(request):
    message = "✅ Test Telegram message from Django!"

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return HttpResponse("Telegram sent!")
    except Exception as e:
        return HttpResponse(f"Telegram FAILED: {e}")