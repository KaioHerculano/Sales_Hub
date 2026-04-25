import pytest
from django.urls import reverse
from outflows.models import Outflow
from products.models import Product
from model_bakery import baker

@pytest.mark.django_db
class TestOutflowViews:
    def test_outflow_list_view(self, auth_client, company):
        product = baker.make(Product, company=company)
        baker.make(Outflow, product=product, company=company)
        url = reverse('outflow_list')
        response = auth_client.get(url)
        assert response.status_code == 200
