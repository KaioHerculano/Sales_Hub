import pytest
from django.urls import reverse
from suppliers.models import Supplier
from rest_framework.test import APIClient
from model_bakery import baker

@pytest.mark.django_db
class TestSupplierViews:
    def test_supplier_list_view(self, auth_client, company):
        baker.make(Supplier, name="Supplier A", company=company)
        url = reverse('supplier_list')
        response = auth_client.get(url)
        assert response.status_code == 200
        assert "Supplier A" in response.content.decode()

    def test_supplier_create_view(self, auth_client, company):
        url = reverse('supplier_create')
        data = {'name': 'New Supplier', 'phone': '123456', 'email': 'test@test.com'}
        response = auth_client.post(url, data)
        assert response.status_code == 302
        assert Supplier.objects.filter(name='New Supplier', company=company).exists()

@pytest.mark.django_db
class TestSupplierAPI:
    def test_supplier_list_api(self, admin_user, company):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        baker.make(Supplier, company=company, _quantity=2)
        url = reverse('supplier-create-list-api-view')
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 2
