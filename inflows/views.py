from rest_framework import generics
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from . import models, forms, serializers
from django.core.exceptions import PermissionDenied


class CompanyObjectMixin:
    """Garante que objetos pertençam à company do usuário."""
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'profile'):
            return queryset.filter(company=self.request.user.profile.company)
        raise PermissionDenied("Usuário não associado a uma company.")


class InflowListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = models.Inflow
    template_name = 'inflow_list.html'
    context_object_name = 'inflows'
    paginate_by = 8
    permission_required = 'inflows.view_inflow'

    def get_queryset(self):
        queryset = super().get_queryset().filter(company=self.request.user.profile.company)
        product = self.request.GET.get('product')

        if product:
            queryset = queryset.filter(product__title__icontains=product)

        return queryset


class InflowCreateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, CreateView):
    model = models.Inflow
    template_name = 'inflow_create.html'
    form_class = forms.InflowForm
    success_url = reverse_lazy('inflow_list')
    permission_required = 'inflows.add_inflow'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
    
        return super().form_valid(form)


class InflowDetailView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = models.Inflow
    template_name = 'inflow_detail.html'
    permission_required = 'inflows.view_inflow'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)


class InflowCreateListAPIView(generics.ListCreateAPIView):
    queryset = models.Inflow.objects.all()
    serializer_class = serializers.InflowSerializer

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.profile.company)


class InflowRetrieveAPIView(generics.RetrieveAPIView):
    queryset = models.Inflow.objects.all()
    serializer_class = serializers.InflowSerializer

    def get_queryset(self):
        return models.Brand.objects.filter(company=self.request.user.profile.company)
