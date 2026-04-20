import pytest
from django.urls import reverse
from sales.models import Budget, Order
from model_bakery import baker

@pytest.mark.django_db
class TestBudgetViews:
    def test_budget_list_view(self, auth_client, company):
        baker.make(Budget, company=company, sale_type='quote', order_status='pending')
        url = reverse('budget_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_budget_pdf_view(self, auth_client, company):
        budget = baker.make(Budget, company=company, sale_type='quote', order_status='pending')
        url = reverse('budget_pdf', kwargs={'pk': budget.pk})
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'

    def test_convert_to_order_post(self, auth_client, company):
        budget = baker.make(Budget, company=company, sale_type='quote', order_status='pending')
        # Create at least one item for conversion
        from sales.models import SaleItem
        from products.models import Product
        product = baker.make(Product, company=company)
        baker.make(SaleItem, sale=budget, product=product, quantity=1, unit_price=10.00, purchase_price=5.00)
        
        url = reverse('budget_convert', kwargs={'pk': budget.pk})
        response = auth_client.post(url)
        
        budget.refresh_from_db()
        assert budget.order_status == 'converted'
        assert Order.objects.filter(company=company, client=budget.client).exists()
        assert response.status_code == 302
