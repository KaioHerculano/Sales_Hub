import pytest
from django.urls import reverse
from products.models import Product
from brands.models import Brand
from categories.models import Category
from model_bakery import baker

@pytest.fixture
def product_setup(company):
    brand = baker.make(Brand, company=company)
    category = baker.make(Category, company=company)
    return brand, category

@pytest.mark.django_db
class TestProductViews:
    def test_product_list_search(self, auth_client, company, product_setup):
        brand, category = product_setup
        baker.make(Product, title="Target Product", company=company, brand=brand, category=category)
        baker.make(Product, title="Other", company=company, brand=brand, category=category)
        
        url = reverse('product_list')
        response = auth_client.get(url + "?product=Target")
        assert "Target Product" in response.content.decode()
        assert "Other" not in response.content.decode()

    def test_product_create_view_post(self, auth_client, company, product_setup):
        brand, category = product_setup
        url = reverse('product_create')
        data = {
            'title': 'New Product',
            'brand': brand.id,
            'category': category.id,
            'cost_price': '10.00',
            'selling_price': '20.00',
            'quantity': 0,
            'serie_number': '123'
        }
        response = auth_client.post(url, data)
        assert response.status_code == 302
        assert Product.objects.filter(title='New Product').exists()

    def test_product_delete_prevented_by_stock(self, auth_client, company, product_setup):
        brand, category = product_setup
        product = baker.make(Product, company=company, brand=brand, category=category, quantity=10)
        url = reverse('product_delete', kwargs={'pk': product.pk})
        
        response = auth_client.post(url)
        assert response.status_code == 200 # Re-renders with error
        assert Product.objects.filter(pk=product.pk).exists()
        assert "Não foi possível excluir" in response.content.decode()

@pytest.mark.django_db
class TestProductPublicAPI:
    def test_public_product_list(self, client, company, product_setup):
        brand, category = product_setup
        baker.make(Product, company=company, brand=brand, category=category, _quantity=2)
        
        url = reverse('public-product-list', kwargs={'company_id': company.id})
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_public_product_detail_not_found(self, client, company):
        url = reverse('public-product-detail', kwargs={'company_id': company.id, 'pk': 999})
        response = client.get(url)
        assert response.status_code == 404
