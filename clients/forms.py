from django import forms
from . import models


class ClientForm(forms.ModelForm):

    class Meta:
        model = models.Client
        fields = ['name', 'date_of_birth', 'address', 'neighborhood','complement', 'telephone', 'email', 'cpf', 'rg']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'complement': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control',}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control',}),
            'rg': forms.TextInput(attrs={'class': 'form-control',}),

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