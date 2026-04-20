import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from categories.models import Category
from products.models import Product
from model_bakery import baker

@pytest.mark.django_db
class TestCategoryViews:
    def test_category_list_view(self, auth_client, company):
        baker.make(Category, name="Cat 1", company=company)
        url = reverse('category_list')
        response = auth_client.get(url)
        assert response.status_code == 200
        assert "Cat 1" in response.content.decode()

    def test_category_create_view(self, auth_client, company):
        url = reverse('category_create')
        data = {'name': 'New Cat', 'description': 'Some desc'}
        response = auth_client.post(url, data)
        assert response.status_code == 302
        assert Category.objects.filter(name='New Cat', company=company).exists()

    def test_category_delete_view_protected(self, auth_client, company):
        category = baker.make(Category, company=company)
        baker.make(Product, category=category, company=company)
        url = reverse('category_delete', kwargs={'pk': category.pk})
        response = auth_client.post(url)
        assert response.status_code == 200
        assert Category.objects.filter(pk=category.pk).exists()
        assert "Não é possível excluir" in response.content.decode()

@pytest.mark.django_db
class TestCategoryAPI:
    def test_category_list_api(self, admin_user, company):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        baker.make(Category, company=company, _quantity=2)
        url = reverse('category-create-list-api-view')
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 2
