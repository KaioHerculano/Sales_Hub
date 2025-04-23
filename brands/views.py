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


class BrandListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = models.Brand
    template_name = 'brand_list.html'
    context_object_name = 'brands'
    paginate_by = 8
    permission_required = 'brands.view_brand'

    def get_queryset(self):
        queryset = super().get_queryset().filter(company=self.request.user.profile.company)
        name = self.request.GET.get('name')

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class BrandCreateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, CreateView):
    model = models.Brand
    template_name = 'brand_create.html'
    form_class = forms.BrandForm
    success_url = reverse_lazy('brand_list')
    permission_required = 'brands.add_brand'

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company
    
        return super().form_valid(form)


class BrandDetailView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = models.Brand
    template_name = 'brand_detail.html'
    permission_required = 'brands.view_brand'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)


class BrandUpdateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, UpdateView):
    model = models.Brand
    template_name = 'brand_update.html'
    form_class = forms.BrandForm
    success_url = reverse_lazy('brand_list')
    permission_required = 'brands.change_brand'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)


class BrandDeleteView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DeleteView):
    model = models.Brand
    template_name = 'brand_delete.html'
    success_url = reverse_lazy('brand_list')
    permission_required = 'brands.delete_brand'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            messages.error(
                request,
                "❌ Não é possível excluir. Há produtos vinculados a esta marca!"
            )
            return self.render_to_response(self.get_context_data())


class BrandCreateListAPIView(generics.ListCreateAPIView):
    queryset = models.Brand.objects.all()
    serializer_class = serializers.BrandSerializer

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.profile.company)


class BrandRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Brand.objects.all()
    serializer_class = serializers.BrandSerializer

    def get_queryset(self):
        return models.Brand.objects.filter(company=self.request.user.profile.company)
