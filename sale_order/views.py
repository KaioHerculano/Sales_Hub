from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from companies.mixins import CompanyObjectMixin
from outflows.models import Outflow
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from sales.utils.pdf import generate_order_pdf
from sales import forms
from sales.models import Sale


class CompanyObjectMixin:
    """Garante que objetos pertençam à company do usuário."""
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'profile'):
            return queryset.filter(company=self.request.user.profile.company)
        raise PermissionDenied("Usuário não associado a uma company.")


class OrderPDFView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = Sale
    permission_required = 'sales.view_order'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        pdf = generate_order_pdf(order)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Context-Disposition"] = f'attachment; filename="pedido_venda_{order.id}.pdf"'
        return response


class OrderListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = Sale
    template_name = 'order_list.html'
    context_object_name = 'orders'
    paginate_by = 8
    permission_required = 'sales.view_order'


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = forms.OrderUpdateForm
    template_name = 'order_create.html'
    success_url = reverse_lazy('order_list')
    permission_required = 'sales.add_order'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items'] = forms.SaleItemFormSet(self.request.POST, prefix="items", user=self.request.user)
        else:
            context['items'] = forms.SaleItemFormSet(prefix="items", user=self.request.user)
        return context
    
    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
        context = self.get_context_data()
        items = context['items']
        for f in items.forms:
            if not f.has_changed():
                f.empty_permitted = True

        self.object = form.save(commit=False)
        self.object.sale_type = 'order'
        if not self.object.order_status:
            self.object.order_status = 'pending'
        if self.request.user.is_authenticated:
            self.object.cashier = self.request.user
        self.object.save()
        
        if items.is_valid():
            items.instance = self.object
            items.save()

            subtotal = sum(item.unit_price * item.quantity for item in self.object.items.all())
            discount_amount = subtotal * (self.object.discount / Decimal("100.00"))
            total = subtotal - discount_amount
            self.object.total = total.quantize(Decimal("0.01"))
            self.object.save(update_fields=["total"])

            if self.object.order_status == 'finalized':
                for item in self.object.items.all():
                    product = item.product
                    discounted_unit_price = (item.unit_price - (item.unit_price * (self.object.discount / Decimal("100.00")))).quantize(Decimal("0.01"))
                    Outflow.objects.create(
                        product=product,
                        quantity=item.quantity,
                        company=self.request.user.profile.company,
                        sale_reference=f"Venda {self.object.id}",
                        description=f"Venda realizada no PDV (Venda {self.object.id}). Preço unitário com desconto: R$ {discounted_unit_price}"
                    )
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        else:
            print(items.errors)
            return self.form_invalid(form)


class OrderDetailView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = Sale
    template_name = 'order_detail.html'
    context_object_name = 'order'
    permission_required = 'sales.view_order'


class OrderUpdateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, UpdateView):
    model = Sale
    form_class = forms.OrderUpdateForm
    template_name = 'order_update.html'
    success_url = reverse_lazy('order_list')
    permission_required = 'sales.change_order'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        self.previous_status = obj.order_status
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale = self.get_object()
        if self.request.POST:
            context['items'] = forms.SaleItemFormSet(self.request.POST, instance=sale, prefix="items")
        else:
            context['items'] = forms.SaleItemFormSet(instance=sale, prefix="items")
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        items = context.get('items')
        self.object = form.save(commit=False)
        previously_finalized = (self.previous_status == 'finalized')
        currently_finalized = (self.object.order_status == 'finalized')
        self.object.save()
        
        if items.is_valid():
            items.instance = self.object
            items.save()
            
            subtotal = sum(item.unit_price * item.quantity for item in self.object.items.all())
            discount_amount = subtotal * (self.object.discount / Decimal("100.00"))
            total = subtotal - discount_amount
            self.object.total = total.quantize(Decimal("0.01"))
            self.object.save(update_fields=["total"])
            
            if self.object.order_status == 'finalized':
                for item in self.object.items.all():
                    product = item.product
                    discounted_unit_price = (item.unit_price - (item.unit_price * (self.object.discount / Decimal("100.00")))).quantize(Decimal("0.01"))
                    Outflow.objects.create(
                        product=product,
                        quantity=item.quantity,
                        company=self.request.user.profile.company,
                        sale_reference=f"Venda {self.object.id}",
                        description=f"Venda realizada no PDV (Venda {self.object.id}). Preço unitário com desconto: R$ {discounted_unit_price}"
                    )
            return HttpResponseRedirect(self.get_success_url())
        else:
            print("Formset errors:", items.errors)
            return self.form_invalid(form)
