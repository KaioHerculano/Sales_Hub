from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.views.generic import ListView
from rest_framework import generics
from companies.mixins import CompanyObjectMixin
from . import models, serializers


class StockMovimentListView(LoginRequiredMixin, PermissionRequiredMixin, CompanyObjectMixin, ListView):
    model = models.StockMoviment
    template_name = 'stock_moviment_list.html'
    context_object_name = 'moviment_entries'
    paginate_by = 8
    permission_required = 'stockmoviment.view_stockmoviment'

    def get_queryset(self):
        queryset = super().get_queryset().filter(company=self.request.user.profile.company)
        search_term = self.request.GET.get('product')

        if search_term:
            queryset = queryset.filter(
                Q(product__title__icontains=search_term)
                | Q(product__serie_number__icontains=search_term)
            )

        return queryset.order_by('-date')


class StockMovimentCreateListAPIView(generics.ListCreateAPIView):
    queryset = models.StockMoviment.objects.all()
    serializer_class = serializers.StockMovimentSerializer

    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.profile.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.profile.company)


class StockMovimentRetrieveAPIView(generics.RetrieveAPIView):
    queryset = models.StockMoviment.objects.all()
    serializer_class = serializers.StockMovimentSerializer

    def get_queryset(self):
        return models.Brand.objects.filter(company=self.request.user.profile.company)
