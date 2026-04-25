import pytest
from django.contrib.auth.models import User
from companies.models import Company, UserProfile
from model_bakery import baker

@pytest.fixture
def company():
    return baker.make(Company)

@pytest.fixture
def admin_user(db, company):
    user = User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='password123'
    )
    UserProfile.objects.create(user=user, company=company, is_company_admin=True)
    return user

@pytest.fixture
def auth_client(client, admin_user):
    client.login(username='admin', password='password123')
    return client
