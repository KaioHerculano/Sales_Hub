from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from rest_framework import generics
from companies.mixins import CompanyObjectMixin
from . import models, forms, serializers


class ClientListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = models.Client
    template_name = 'client_list.html'
    context_object_name = 'clients'
    paginate_by = 8
    permission_required = 'clients.view_client'

    def get_queryset(self):
        queryset = super().get_queryset().filter(company=self.request.user.profile.company)
        name = self.request.GET.get('name')

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, CreateView):
    model = models.Client
    template_name = 'client_create.html'
    form_class = forms.ClientForm
    success_url = reverse_lazy('client_list')
    permission_required = 'clients.add_client'

    def form_valid(self, form):
        form.instance.company = self.request.user.profile.company

        return super().form_valid(form)


class ClientDetailView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DetailView):
    model = models.Client
    template_name = 'client_detail.html'
    permission_required = 'clients.view_client'


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, UpdateView):
    model = models.Client
    template_name = 'client_update.html'
    form_class = forms.ClientForm
    success_url = reverse_lazy('client_list')
    permission_required = 'clients.change_client'


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, DeleteView):
    model = models.Client
    template_name = 'client_delete.html'
    success_url = reverse_lazy('client_list')
    permission_required = 'clients.delete_client'


class ClientCreateListAPIView(generics.ListCreateAPIView):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.profile.company)


class ClientRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer

    def get_queryset(self):
        return models.Brand.objects.filter(company=self.request.user.profile.company)
