from rest_framework import generics
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from . import models, forms, serializers


class ClientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Client
    template_name = 'client_list.html'
    context_object_name = 'clients'
    paginate_by = 8
    permission_required = 'clients.view_client'

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Client
    template_name = 'client_create.html'
    form_class = forms.ClientForm
    success_url = reverse_lazy('client_list')
    permission_required = 'clients.add_client'


class ClientDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Client
    template_name = 'client_detail.html'
    permission_required = 'clients.view_client'


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Client
    template_name = 'client_update.html'
    form_class = forms.ClientForm
    success_url = reverse_lazy('client_list')
    permission_required = 'clients.change_client'


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Client
    template_name = 'client_delete.html'
    success_url = reverse_lazy('client_list')
    permission_required = 'clients.delete_client'


class ClientCreateListAPIView(generics.ListCreateAPIView):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer


class ClientRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer
