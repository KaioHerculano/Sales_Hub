from django import forms
from . import models
from brands.models import Brand
from categories.models import Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = models.Product
        fields = ['title', 'brand', 'category', 'serie_number', 'cost_price', 'selling_price', 'description', 'photo',]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'serie_number': forms.TextInput(attrs={'class': 'form-control'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'data-mask': '000.000.000,00', 'data-mask-reverse': 'True'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'data-mask': '000.000.000,00', 'data-mask-reverse': 'True'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        }
        labels = {
            'title': 'Titulo',
            'brand': 'Marca',
            'category': 'Categoria',
            'serie_number': 'Numero de Serie',
            'cost_price': 'Preço de Custo',
            'selling_price': 'Preço de Venda',
            'description': 'Descrição',
            'photo': 'Foto do Produto',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile') and user.profile.company:
            company = user.profile.company
            self.fields['brand'].queryset = Brand.objects.filter(company=company)
            self.fields['category'].queryset = Category.objects.filter(company=company)
