from django import forms
from django.forms import inlineformset_factory
from .models import Sale, SaleItem

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ('id', 'product', 'quantity', 'unit_price')
        widgets = {
            'id': forms.HiddenInput(), 
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

SaleItemFormSet = inlineformset_factory(
    Sale, SaleItem,
    form=SaleItemForm,
    fields=('id', 'product', 'quantity', 'unit_price'),
    extra=1,
    can_delete=True
)

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['client', 'discount', 'seller', 'payment_method',]
        widgets = {
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Discount (%)', 'min': '0', 'max': '100','step': '0.01'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'seller': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }
        

class OrderUpdateForm(SaleForm):
    class Meta(SaleForm.Meta):
        model = Sale
        fields = ['client', 'discount', 'payment_method', 'seller', 'order_status', 'expiration_date']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Discount (%)', 'min': '0', 'max': '100','step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'seller': forms.Select(attrs={'class': 'form-control'}),
            'order_status': forms.Select(attrs={'class': 'form-control'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'id' in self.fields:
            self.fields['id'].required = False


class BudgetForm(OrderUpdateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'order_status' in self.fields:
            self.fields['order_status'].choices = [
                choice for choice in self.fields['order_status'].choices if choice[0] != 'finalized'
            ]