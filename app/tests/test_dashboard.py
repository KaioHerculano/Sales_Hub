import pytest
from django.urls import reverse
from model_bakery import baker
from sales.models import Sale
from products.models import Product

@pytest.mark.django_db
class TestDashboard:
    def test_dashboard_view(self, auth_client, company, admin_user):
        from clients.models import Client
        # Create some data to exercise metrics
        product = baker.make(Product, company=company, quantity=5, cost_price=10.00, selling_price=20.00)
        client = baker.make(Client, company=company, telephone='65999999999')
        sale = baker.make(Sale, company=company, order_status='finalized', total=500.00, client=client, seller=admin_user)
        
        url = reverse('home')
        response = auth_client.get(url)
        assert response.status_code == 200
        # Check if metrics are in context
        assert 'sales_metrics' in response.context
        assert 'product_metrics' in response.context
        assert 'top_clients' in response.context
        assert 'value_by_seller' in response.context
