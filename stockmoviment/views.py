from django.views.generic import ListView
from django.db.models import Q
from .models import StockMoviment



class StockMovimentListView(ListView):
    model = StockMoviment
    template_name = 'stock_moviment_list.html'
    context_object_name = 'moviment_entries'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('product')

        if search_term:
            queryset = queryset.filter(
                Q(product__title__icontains=search_term) |
                Q(product__brand__name__icontains=search_term)
            )

        return queryset.order_by('-date')
