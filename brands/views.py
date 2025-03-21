from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.urls import reverse_lazy
from . import models, forms


class BrandListView(ListView):
    model = models.Brand
    template_name = 'brand_list.html'
    context_object_name = 'brands'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class BrandCreateView(CreateView):
    model = models.Brand
    template_name = 'brand_create.html'
    form_class = forms.BrandForm
    success_url = reverse_lazy('brand_list')


class BrandDetailView(DetailView):
    model = models.Brand
    template_name = 'brand_detail.html'

class BrandUpdateView(UpdateView):
    model = models.Brand
    template_name = 'brand_update.html'
    form_class = forms.BrandForm
    success_url = reverse_lazy('brand_list')


class BrandDeleteView(DeleteView):
    model = models.Brand
    template_name = 'brand_delete.html'
    success_url = reverse_lazy('brand_list')

    def form_valid(self, form):
        try:

            self.object.delete()
            messages.success(self.request, "Marca excluída com sucesso!")
            return super().form_valid(form)
        except ProtectedError:

            messages.error(
                self.request,
                "❌ Não é possível excluir. Há produtos vinculados a esta marca!"
            )

            return self.render_to_response(self.get_context_data())