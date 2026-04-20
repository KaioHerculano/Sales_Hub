import pytest
from model_bakery import baker
from outflows.models import Outflow
from products.models import Product

@pytest.mark.django_db
def test_outflow_signal_updates_stock(company):
    product = baker.make(Product, quantity=10, company=company)
    # Create outflow
    baker.make(Outflow, product=product, quantity=3, company=company)
    
    product.refresh_from_db()
    assert product.quantity == 7
