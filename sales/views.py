from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from . import models
from .forms import SaleForm, SaleItemFormSet
from products.models import Product  
from outflows.models import Outflow
import json
from django.http import JsonResponse
from django.views import View
from decimal import Decimal

class GetProductPriceView(View):
    def get(self, request):
        product_id = request.GET.get("product_id")
        try:
            product = Product.objects.get(pk=product_id)
            return JsonResponse({'price': str(product.selling_price)})
        except Product.DoesNotExist:
            return JsonResponse({'price': ''})  # Certifique-se de que o modelo Outflow esteja definido corretamente


class SaleCreateView(CreateView):
    model = models.Sale
    form_class = SaleForm
    template_name = 'sale_create.html'
    success_url = reverse_lazy('sale_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items'] = SaleItemFormSet(self.request.POST)
        else:
            context['items'] = SaleItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        self.object = form.save(commit=False)
        if not self.object.cashier and self.request.user.is_authenticated:
            self.object.cashier = self.request.user
        self.object.save()
        if items.is_valid():
            items.instance = self.object
            items.save()
            
            # Calcula o subtotal sem aplicar desconto individualmente
            subtotal = sum(item.unit_price * item.quantity for item in self.object.items.all())
            discount_factor = (Decimal("100.00") - self.object.discount) / Decimal("100.00")
            total = subtotal * discount_factor
            self.object.total = total.quantize(Decimal("0.01"))
            self.object.save(update_fields=["total"])
            
            for item in self.object.items.all():
                product = item.product
                # Atualiza o estoque do produto
                product.quantity -= item.quantity
                product.save()
                
                # Calcula o preço unitário com desconto para este item
                discounted_unit_price = (item.unit_price * discount_factor).quantize(Decimal("0.01"))
                
                # Cria a saída (Outflow) com o valor unitário com desconto
                Outflow.objects.create(
                    product=product,
                    quantity=item.quantity,
                    sale_reference=f"Venda {self.object.id}",
                    description=f"Venda realizada no PDV (Venda {self.object.id}). Preço unitário com desconto: R$ {discounted_unit_price}"
                )
        return super().form_valid(form)

    
class SaleListView(ListView):
    model = models.Sale
    template_name = 'sale_list.html'
    context_object_name = 'sales'


class SaleDetailView(DetailView):
    model = models.Sale
    template_name = "sale_detail.html"
    context_object_name = "sale"