from django.urls import path
from . import views


urlpatterns=[
    path('stockmoviment/ist/', views.StockMovimentListView.as_view(), name='stock_moviment_list'),
]