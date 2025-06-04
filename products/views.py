from app import metrics
from rest_framework import generics
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from . import models, forms, serializers
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import ProductSerializer


class CompanyObjectMixin:

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'profile'):
            return queryset.filter(company=self.request.user.profile.company)
        raise PermissionDenied("Usuário não associado a uma company.")


class PublicProductListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, company_id):
        products = models.Product.objects.filter(company_id=company_id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = models.Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 8
    permission_required = 'products.view_product'

    def get_queryset(self):
        queryset = super().get_queryset().filter(company=self.request.user.profile.company)
        search_term = self.request.GET.get('product')

        if search_term:
            queryset = queryset.filter(
                Q(title__icontains=search_term)
                | Q(brand__name__icontains=search_term)
                | Q(numbering__icontains=search_term)
                | Q(serie_number__icontains=search_term)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.profile.company
        context['product_metrics'] = metrics.get_product_metrics(company)
        return context


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, CreateView):
    model = models.Product
    template_name = 'product_create.html'
    form_class = forms.ProductForm
    success_url = reverse_lazy('product_list')
    permission_required = 'products.add_product'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
    
        return super().form_valid(form)


class ProductDetailView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = models.Product
    template_name = 'product_detail.html'
    permission_required = 'products.view_product'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, UpdateView):
    model = models.Product
    template_name = 'product_update.html'
    form_class = forms.ProductForm
    success_url = reverse_lazy('product_list')
    permission_required = 'products.change_product'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)


class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DeleteView):
    model = models.Product
    template_name = 'product_delete.html'
    success_url = reverse_lazy('product_list')
    permission_required = 'products.delete_product'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        error_msg = None

        if self.object.quantity > 0:
            error_msg = (
                f"Não foi possível excluir {self.object.title}. "
                f"Estoque atual: {self.object.quantity} unidades."
            )
        try:
            has_inflows = self.object.inflow_set.exists()
            has_outflows = self.object.outflow_set.exists()
        except AttributeError:
            has_inflows = self.object.inflows.exists()
            has_outflows = self.object.outflows.exists()

        if has_inflows or has_outflows:
            error_msg = (
                f"❌ Não foi possível excluir {self.object.title}. "
                f"Estoque atual: {self.object.quantity} unidades."
            )
        if error_msg:
            messages.error(request, error_msg)
            return self.get(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)


class ProductCreateListAPIView(generics.ListCreateAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.profile.company)


class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        return models.Product.objects.filter(company=self.request.user.profile.company)
