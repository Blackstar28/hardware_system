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
        return redirect('generate_receipt_pdf', sale_id=sale.id)

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
            from_email='yourshop@example.com',
            recipient_list=['youremail@example.com'],
            fail_silently=False,
        )
    # After saving the sale and reducing stock
check_and_notify_low_stock()
