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


class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = models.Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    paginate_by = 8
    permission_required = 'categories.view_category'

    def get_queryset(self):
        queryset = super().get_queryset().filter(company=self.request.user.profile.company)
        name = self.request.GET.get('name')

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, CreateView):
    model = models.Category
    template_name = 'category_create.html'
    form_class = forms.CategoryForm
    success_url = reverse_lazy('category_list')
    permission_required = 'categories.add_category'

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company

        return super().form_valid(form)


class CategoryDetailView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = models.Category
    template_name = 'category_detail.html'
    permission_required = 'categories.view_category'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, UpdateView):
    model = models.Category
    template_name = 'category_update.html'
    form_class = forms.CategoryForm
    success_url = reverse_lazy('category_list')
    permission_required = 'categories.change_category'

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DeleteView):
    model = models.Category
    template_name = 'category_delete.html'
    success_url = reverse_lazy('category_list')
    permission_required = 'categories.delete_category'

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
                "❌ Não é possível excluir. Há produtos vinculados a esta categoria!"
            )

            return self.render_to_response(self.get_context_data())


class CategoryCreateListAPIView(generics.ListCreateAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.profile.company)


class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_queryset(self):
        return models.Brand.objects.filter(company=self.request.user.profile.company)
