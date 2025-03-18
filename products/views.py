from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from . import models, forms
from app import metrics


class ProductListView(ListView):
    model = models.Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('product')

        if search_term:
            queryset = queryset.filter(
                Q(title__icontains=search_term) |
                Q(brand__name__icontains=search_term) |
                Q(numbering__icontains=search_term) |
                Q(serie_number__icontains=search_term)
            )

        return queryset
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['product_metrics'] = metrics.get_product_metrics()

        return context


class ProductCreateView(CreateView):
    model = models.Product
    template_name = 'product_create.html'
    form_class = forms.ProductForm
    success_url = reverse_lazy('product_list')


class ProductDetailView(DetailView):
    model = models.Product
    template_name = 'product_detail.html'


class ProductUpdateView(UpdateView):
    model = models.Product
    template_name = 'product_update.html'
    form_class = forms.ProductForm
    success_url = reverse_lazy('product_list')


class ProductDeleteView(DeleteView):
    model = models.Product
    template_name = 'product_delete.html'
    success_url = reverse_lazy('product_list')

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
                f"Não foi possível excluir {self.object.title}. "
                f"Estoque atual: {self.object.quantity} unidades."
            )
        
        if error_msg:
            messages.error(request, error_msg)
            return self.get(request, *args, **kwargs)
        
        return super().post(request, *args, **kwargs)
