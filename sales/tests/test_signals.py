import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError
from model_bakery import baker
from sales.models import Budget

@pytest.mark.django_db
def test_budget_expiration_signal(company):
    # Create an already expired date
    expired_date = timezone.now().date() - timezone.timedelta(days=1)
    
    # baker.make calls .save(), which triggers the signal
    with pytest.raises(ValidationError) as excinfo:
        baker.make(Budget, company=company, expiration_date=expired_date, sale_type='quote', order_status='pending')
    
    assert "Orçamento expirado não pode ser alterado." in str(excinfo.value)
