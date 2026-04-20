import pytest
from model_bakery import baker
from inflows.models import Inflow
from products.models import Product

@pytest.mark.django_db
def test_inflow_signal_updates_stock(company):
    product = baker.make(Product, quantity=10, company=company)
    # Create inflow
    baker.make(Inflow, product=product, quantity=5, company=company)
    
    product.refresh_from_db()
    assert product.quantity == 15
