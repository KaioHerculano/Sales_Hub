from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={'class': 'form-control', 'placeholder': 'DD/MM/AAAA'}
        ),
        input_formats=['%d/%m/%Y', '%d%m%Y'],
        required=False
    )

    class Meta:
        model = Client
        fields = ['name', 'date_of_birth', 'address', 'neighborhood', 'complement', 'telephone', 'email', 'cpf', 'rg']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'complement': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Name',
            'date_of_birth': 'Data de Nascimento',
            'address': 'Endereço',
            'neighborhood': 'Bairro',
            'complement': 'Complemento',
            'telephone': 'Telefone',
            'email': 'Email',
            'cpf': 'CPF',
            'rg': 'RG',
        }
