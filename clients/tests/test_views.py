import pytest
from django.urls import reverse
from clients.models import Client
from rest_framework.test import APIClient
from model_bakery import baker

@pytest.mark.django_db
class TestClientViews:
    def test_client_list_view(self, auth_client, company):
        baker.make(Client, name="Client A", company=company, telephone='65999999999')
        url = reverse('client_list')
        response = auth_client.get(url)
        assert response.status_code == 200
        assert "Client A" in response.content.decode()

    def test_client_create_view(self, auth_client, company):
        url = reverse('client_create')
        data = {'name': 'New Client', 'telephone': '65999999999', 'email': 'test@test.com'}
        response = auth_client.post(url, data)
        assert response.status_code == 302
        assert Client.objects.filter(name='New Client', company=company).exists()

@pytest.mark.django_db
class TestClientAPI:
    def test_client_list_api(self, admin_user, company):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        baker.make(Client, company=company, telephone='65999999999', _quantity=2)
        url = reverse('client-create-list-api-view')
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 2
