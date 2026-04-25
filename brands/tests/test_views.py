import pytest
from django.urls import reverse
from brands.models import Brand
from products.models import Product
from model_bakery import baker

@pytest.mark.django_db
class TestBrandViews:
    def test_brand_list_view(self, auth_client, company):
        baker.make(Brand, name="Brand 1", company=company)
        baker.make(Brand, name="Other", company=company)
        
        url = reverse('brand_list')
        response = auth_client.get(url)
        assert response.status_code == 200
        assert "Brand 1" in response.content.decode()
        
        # Test filter
        response = auth_client.get(url + "?name=Brand")
        assert "Brand 1" in response.content.decode()
        assert "Other" not in response.content.decode()

    def test_brand_create_view(self, auth_client, company):
        url = reverse('brand_create')
        data = {'name': 'New Brand', 'description': 'Some desc'}
        response = auth_client.post(url, data)
        assert response.status_code == 302
        assert Brand.objects.filter(name='New Brand', company=company).exists()

    def test_brand_update_view(self, auth_client, company):
        brand = baker.make(Brand, name="Old Name", company=company)
        url = reverse('brand_update', kwargs={'pk': brand.pk})
        data = {'name': 'Updated Name'}
        response = auth_client.post(url, data)
        assert response.status_code == 302
        brand.refresh_from_db()
        assert brand.name == 'Updated Name'

    def test_brand_delete_view_success(self, auth_client, company):
        brand = baker.make(Brand, company=company)
        url = reverse('brand_delete', kwargs={'pk': brand.pk})
        response = auth_client.post(url)
        assert response.status_code == 302
        assert not Brand.objects.filter(pk=brand.pk).exists()

    def test_brand_delete_view_protected(self, auth_client, company):
        brand = baker.make(Brand, company=company)
        # Link a product to prevent deletion (ProtectedError)
        baker.make(Product, brand=brand, company=company)
        
        url = reverse('brand_delete', kwargs={'pk': brand.pk})
        response = auth_client.post(url)
        assert response.status_code == 200 # Returns to delete page with error
        assert Brand.objects.filter(pk=brand.pk).exists()
        assert "Não é possível excluir" in response.content.decode()
