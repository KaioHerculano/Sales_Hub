from django.urls import path
from . import views

urlpatterns = [
    path('budgets/list/', views.BudgetListView.as_view(), name='budget_list'),
    path('budgets/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budgets/<int:pk>/', views.BudgetDetailView.as_view(), name='budget_detail'),
    path('budgets/<int:pk>/update/', views.BudgetUpdateView.as_view(), name='budget_update'),
    path('budgets/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),
    path('budgets/<int:pk>/convert/', views.ConvertToOrderView.as_view(), name='budget_convert'),
    path('budget/<int:pk>/pdf/', views.BudgetPDFView.as_view(), name='budget_pdf'),
]