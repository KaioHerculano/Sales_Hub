from rest_framework import generics
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView
from django.db.models import Q
from . import models, serializers


class StockMovimentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.StockMoviment
    template_name = 'stock_moviment_list.html'
    context_object_name = 'moviment_entries'
    paginate_by = 8
    permission_required = 'stockmoviment.view_stockmoviment'

    def get_queryset(self):
        queryset = super().get_queryset()
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


class StockMovimentRetrieveAPIView(generics.RetrieveAPIView):
    queryset = models.StockMoviment.objects.all()
    serializer_class = serializers.StockMovimentSerializer
