from django import forms
from .models import Product
from django.forms import formset_factory

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
