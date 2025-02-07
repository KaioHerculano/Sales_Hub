from django.urls import path
from .views import brand_list_view, brand_create_view, brand_delete_view

urlpatterns = [
    path('', brand_list_view, name='brand_list'),
    path('create/', brand_create_view, name='brand_create'),
    path('<int:pk>/delete/', brand_delete_view, name='brand_delete'),
]
