from django import forms
from . import models


class ProductForm(forms.ModelForm):

    class Meta:
        model = models.Product
        fields = ['title', 'brand', 'category', 'numbering','serie_number', 'cost_price', 'selling_price', 'description',]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'category':forms.Select(attrs={'class': 'form-control'}),
            'numbering': forms.Select(attrs={'class': 'form-control'}),
            'serie_number': forms.TextInput(attrs={'class': 'form-control'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'data-mask': '000.000.000,00', 'data-mask-reverse': 'True'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'data-mask': '000.000.000,00', 'data-mask-reverse': 'True'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),

        }
        labels = {
            'title': 'Titulo',
            'brand': 'Marca',
            'category': 'Categoria',
            'numbering': 'Numeração',
            'serie_number': 'Numero de Serie',
            'cost_price': 'Preço de Custo',
            'selling_price': 'Preço de Venda',
            'description': 'Descrição',
        }