from django.urls import path
from . import views


urlpatterns=[
    path('stockmoviment/ist/', views.StockMovimentListView.as_view(), name='stock_moviment_list'),

    path('api/v1/stockmoviment/', views.StockMovimentCreateListAPIView.as_view(), name='stockmoviment-create-list-api-view'),
    path('api/v1/stockmoviment/<int:pk>/', views.StockMovimentRetrieveAPIView.as_view(), name='stockmoviment-detail-api-view'),
]