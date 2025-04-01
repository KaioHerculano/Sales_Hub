from django import forms
from django.forms import inlineformset_factory
from .models import Sale, SaleItem

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['client', 'discount', 'seller', 'payment_method']
        widgets = {
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Discount (%)', 'min': '0', 'max': '100'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'seller': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }

SaleItemFormSet = inlineformset_factory(
    Sale, SaleItem,
    fields=('product', 'quantity', 'unit_price'),
    extra=1,
    can_delete=True,
    widgets={
        'product': forms.Select(attrs={'class': 'form-control'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)
