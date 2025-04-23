from rest_framework import generics
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.urls import reverse_lazy
from . import models, forms, serializers
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied


class CompanyObjectMixin:
    """Garante que objetos pertençam à company do usuário."""
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'profile'):
            return queryset.filter(company=self.request.user.profile.company)
        raise PermissionDenied("Usuário não associado a uma company.")


class SupplierListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = models.Supplier
    template_name = 'supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 8
    permission_required = 'suppliers.view_supplier'

    def get_queryset(self):
        queryset = super().get_queryset().filter(company=self.request.user.profile.company)
        name = self.request.GET.get('name')

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class SupplierCreateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, CreateView):
    model = models.Supplier
    template_name = 'supplier_create.html'
    form_class = forms.SupplierForm
    success_url = reverse_lazy('supplier_list')
    permission_required = 'suppliers.add_supplier'

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
    
        return super().form_valid(form)


class SupplierDetailView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = models.Supplier
    template_name = 'supplier_detail.html'
    permission_required = 'suppliers.view_supplier'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)


class SupplierUpdateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, UpdateView):
    model = models.Supplier
    template_name = 'supplier_update.html'
    form_class = forms.SupplierForm
    success_url = reverse_lazy('supplier_list')
    permission_required = 'suppliers.change_supplier'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)


class SupplierDeleteView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DeleteView):
    model = models.Supplier
    template_name = 'supplier_delete.html'
    success_url = reverse_lazy('supplier_list')
    permission_required = 'suppliers.delete_supplier'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def form_valid(self, form):
        try:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        except ProtectedError:

            messages.error(
                self.request,
                "❌ Não é possível excluir. Há produtos vinculados a este fornecedor!"
            )

            return self.render_to_response(self.get_context_data())


class SupplierCreateListAPIView(generics.ListCreateAPIView):
    queryset = models.Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.profile.company)


class SupplierRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer

    def get_queryset(self):
        return models.Brand.objects.filter(company=self.request.user.profile.company)
