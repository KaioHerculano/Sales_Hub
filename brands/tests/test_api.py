import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from brands.models import Brand
from model_bakery import baker

@pytest.fixture
def api_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client

@pytest.mark.django_db
class TestBrandAPI:
    def test_brand_list_api(self, api_client, company):
        baker.make(Brand, company=company, _quantity=3)
        url = reverse('brand-create-list-api-view')
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 3

    def test_brand_create_api(self, api_client, company):
        url = reverse('brand-create-list-api-view')
        data = {'name': 'API Brand', 'description': 'API test'}
        response = api_client.post(url, data)
        assert response.status_code == 201
        assert Brand.objects.filter(name='API Brand', company=company).exists()

    def test_brand_detail_api(self, api_client, company):
        brand = baker.make(Brand, company=company)
        url = reverse('brand-detail-api-view', kwargs={'pk': brand.pk})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['name'] == brand.name
