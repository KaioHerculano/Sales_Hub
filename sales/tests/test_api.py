import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from model_bakery import baker
from sales.models import Sale
from products.models import Product

@pytest.mark.django_db
class TestSaleAPI:
    def test_sale_list_api(self, admin_user, company):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        baker.make(Sale, company=company, _quantity=2)
        url = reverse('sale-create-list-api-view')
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_sale_create_api(self, admin_user, company):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        product = baker.make(Product, company=company, selling_price=10.00)
        
        url = reverse('sale-create-list-api-view')
        data = {
            'discount': 0,
            'sale_type': 'order',
            'order_status': 'finalized',
            'items': [
                {'product': product.id, 'quantity': 2, 'unit_price': 10.00}
            ]
        }
        response = client.post(url, data, format='json')
        assert response.status_code == 201
        assert Sale.objects.filter(company=company).count() == 1
        assert Sale.objects.first().total == 20.00
