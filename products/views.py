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
import os # Importar para usar em debug se necessário
from django.conf import settings # Importar para aceder a MEDIA_ROOT em debug

class CompanyObjectMixin:

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'profile'):
            return queryset.filter(company=self.request.user.profile.company)
        raise PermissionDenied("Usuário não associado a uma company.")


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
                # | Q(numbering__icontains=search_term) # 'numbering' não está no modelo Product
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
        # DEBUG: Verifica se o ficheiro da foto está em request.FILES
        if 'photo' in self.request.FILES:
            print(f"DEBUG (CreateView): Ficheiro de foto recebido: {self.request.FILES['photo'].name}")
            print(f"DEBUG (CreateView): Tamanho do ficheiro: {self.request.FILES['photo'].size} bytes")
        else:
            print("DEBUG (CreateView): NENHUM ficheiro de foto em request.FILES.")
        
        # DEBUG: Verifica a configuração de MEDIA_ROOT
        print(f"DEBUG (CreateView): MEDIA_ROOT configurado para: {settings.MEDIA_ROOT}")
        if not os.path.exists(settings.MEDIA_ROOT):
            print(f"DEBUG (CreateView): O diretório MEDIA_ROOT NÃO EXISTE: {settings.MEDIA_ROOT}")
        elif not os.access(settings.MEDIA_ROOT, os.W_OK):
            print(f"DEBUG (CreateView): O diretório MEDIA_ROOT NÃO TEM PERMISSÕES DE ESCRITA: {settings.MEDIA_ROOT}")
        else:
            print(f"DEBUG (CreateView): O diretório MEDIA_ROOT EXISTE e tem permissões de escrita.")


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

    def form_valid(self, form):
        # DEBUG: Verifica se o ficheiro da foto está em request.FILES
        if 'photo' in self.request.FILES:
            print(f"DEBUG (UpdateView): Ficheiro de foto recebido: {self.request.FILES['photo'].name}")
            print(f"DEBUG (UpdateView): Tamanho do ficheiro: {self.request.FILES['photo'].size} bytes")
        else:
            print("DEBUG (UpdateView): NENHUM ficheiro de foto em request.FILES.")

        # DEBUG: Verifica a configuração de MEDIA_ROOT
        print(f"DEBUG (UpdateView): MEDIA_ROOT configurado para: {settings.MEDIA_ROOT}")
        if not os.path.exists(settings.MEDIA_ROOT):
            print(f"DEBUG (UpdateView): O diretório MEDIA_ROOT NÃO EXISTE: {settings.MEDIA_ROOT}")
        elif not os.access(settings.MEDIA_ROOT, os.W_OK):
            print(f"DEBUG (UpdateView): O diretório MEDIA_ROOT NÃO TEM PERMISSÕES DE ESCRITA: {settings.MEDIA_ROOT}")
        else:
            print(f"DEBUG (UpdateView): O diretório MEDIA_ROOT EXISTE e tem permissões de escrita.")
            
        return super().form_valid(form)


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


class PublicProductListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, company_id):
        products = models.Product.objects.filter(company_id=company_id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class PublicProductDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, company_id, pk):
        try:
            product = models.Product.objects.get(company_id=company_id, pk=pk)
        except models.Product.DoesNotExist:
            return Response({'detail': 'Produto não encontrado.'}, status=404)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


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

