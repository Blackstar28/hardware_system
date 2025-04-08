from django import forms
from django.forms import formset_factory, inlineformset_factory, modelformset_factory
from .models import Product, PurchaseOrder, PurchaseOrderItem

# POS Form for front-end sales
class POSItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'product-select'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'qty-input'})
    )

POSFormSet = formset_factory(POSItemForm, extra=1, can_delete=True)

# Purchase Order
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier']

# Inline formset for purchase order items
POItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    fields=['product', 'quantity', 'unit_price'],
    extra=1,
    can_delete=True
)

PurchaseOrderItemFormSet = modelformset_factory(
    PurchaseOrderItem,
    fields=('product', 'quantity', 'unit_price'),
    extra=1,
    can_delete=True
)