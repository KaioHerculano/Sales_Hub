import pytest
from django.urls import reverse
from inflows.models import Inflow
from products.models import Product
from model_bakery import baker

@pytest.mark.django_db
class TestInflowViews:
    def test_inflow_list_view(self, auth_client, company):
        product = baker.make(Product, company=company)
        baker.make(Inflow, product=product, company=company)
        url = reverse('inflow_list')
        response = auth_client.get(url)
        assert response.status_code == 200
