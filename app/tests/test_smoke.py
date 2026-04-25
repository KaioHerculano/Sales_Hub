import pytest
from django.urls import reverse
from model_bakery import baker
from django.contrib.auth.models import User
from companies.models import Company, UserProfile

@pytest.fixture
def logged_in_user(client):
    user = User.objects.create_superuser(username='admin', password='password', email='admin@test.com')
    # Create a company because most views depend on it
    company = baker.make(Company)
    UserProfile.objects.create(user=user, company=company)
    client.login(username='admin', password='password')
    return user

@pytest.mark.django_db
class TestSmokeViews:
    def test_home_page_status_code(self, client, logged_in_user):
        url = reverse('home')
        response = client.get(url)
        assert response.status_code == 200

    def test_product_list_status_code(self, client, logged_in_user):
        url = reverse('product_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_supplier_list_status_code(self, client, logged_in_user):
        url = reverse('supplier_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_client_list_status_code(self, client, logged_in_user):
        url = reverse('client_list')
        response = client.get(url)
        assert response.status_code == 200
