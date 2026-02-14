from decimal import Decimal
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from rest_framework import generics
from app import metrics
from clients.models import Client
from companies.mixins import CompanyObjectMixin
from outflows.models import Outflow
from products.models import Product
from . import forms, models, serializers
from .models import Sale
from .utils.pdf import generate_invoice_pdf

class InvoicePDFView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = Sale
    permission_required = 'sales.view_sale'

    def get(self, request, *args, **kwargs):
        sale = self.get_object()
        pdf = generate_invoice_pdf(sale)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="nota_fiscal_{sale.id}.pdf"'
        return response      



class GetProductPriceView(View):
    def get(self, request):
        product_id = request.GET.get("product_id")
        try:
            product = Product.objects.get(pk=product_id)
            return JsonResponse({'price': str(product.selling_price)})
        except Product.DoesNotExist:
            return JsonResponse({'price': ''})


class SaleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, CreateView):
    model = Sale
    form_class = forms.SaleForm
    template_name = 'sale_create.html'
    success_url = reverse_lazy('sale_list')
    permission_required = 'sales.add_sale'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items'] = forms.SaleItemFormSet(self.request.POST, user=self.request.user)
        else:
            context['items'] = forms.SaleItemFormSet(user=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']

        with transaction.atomic():
            form.instance.company = self.request.user.profile.company
            if not form.instance.cashier:
                form.instance.cashier = self.request.user

            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()

                self.object.update_totals()
                self.object.finalize()

            else:
                return self.form_invalid(form)


        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        context = self.get_context_data()
        return self.render_to_response(self.get_context_data(form=form))


class SaleListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = models.Sale
    template_name = 'sale_list.html'
    context_object_name = 'sales'
    paginate_by = 8
    permission_required = 'sales.view_sale'

    def get_queryset(self):
        queryset = super().get_queryset().filter(company=self.request.user.profile.company)
        client_id = self.request.GET.get("client")
        if client_id:
            queryset = queryset.filter(client__id=client_id)
        queryset = queryset.filter(
            Q(sale_type='quote') | 
            (Q(sale_type='order') & Q(order_status='finalized'))
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.profile.company
        context['clients'] = Client.objects.filter(company=company)
        context['sales_metrics'] = metrics.get_sales_metrics(company) 
        return context


class SaleDetailView(LoginRequiredMixin, CompanyObjectMixin, DetailView):
    model = models.Sale
    template_name = "sale_detail.html"
    context_object_name = "sale"
    permission_required = 'sales.view_sale'


class SaleCreateListAPIView(generics.ListCreateAPIView):
    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.profile.company)


class SaleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer

    def get_queryset(self):
        return models.Brand.objects.filter(company=self.request.user.profile.company)
