import pytest
from model_bakery import baker
from products.models import Product

@pytest.mark.django_db
class TestProductModel:
    def test_product_margin_calculation(self):
        # Setup: Create a product using model_bakery
        product = baker.make(
            Product,
            cost_price=50.00,
            selling_price=120.00
        )
        
        # Action: Check margin property
        # Expected: 120 - 50 = 70
        assert product.margin == 70.00

    def test_product_margin_with_zero_prices(self):
        product = baker.make(
            Product,
            cost_price=0.00,
            selling_price=0.00
        )
        assert product.margin == 0.00

    def test_product_str_representation(self):
        product = baker.make(Product, title="Notebook Gamer")
        assert str(product) == "Notebook Gamer"
