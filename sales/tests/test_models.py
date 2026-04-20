import pytest
from decimal import Decimal
from model_bakery import baker
from sales.models import Sale, SaleItem, Budget, Order
from products.models import Product
from outflows.models import Outflow

@pytest.mark.django_db
class TestSaleModels:
    def test_sale_total_calculation(self, company):
        product = baker.make(Product, selling_price=Decimal("100.00"), company=company)
        sale = baker.make(Sale, discount=Decimal("10.00"), company=company)
        baker.make(SaleItem, sale=sale, product=product, quantity=2, unit_price=Decimal("100.00"))
        
        sale.update_totals()
        # (2 * 100) * 0.9 = 180
        assert sale.total == Decimal("180.00")

    def test_sale_finalize_creates_outflows(self, company):
        product = baker.make(Product, quantity=10, company=company)
        sale = baker.make(Sale, company=company, order_status='finalized')
        baker.make(SaleItem, sale=sale, product=product, quantity=3, unit_price=Decimal("50.00"))
        
        sale.finalize()
        
        product.refresh_from_db()
        assert product.quantity == 7
        assert Outflow.objects.filter(sale_reference=f"Venda {sale.id}").exists()

    def test_budget_conversion_to_order(self, company):
        budget = baker.make(Budget, company=company, sale_type='quote', order_status='pending')
        product = baker.make(Product, company=company)
        baker.make(SaleItem, sale=budget, product=product, quantity=1, unit_price=Decimal("100.00"))
        
        order = budget.convert_to_order()
        
        assert isinstance(order, Order)
        assert order.sale_type == 'order'
        assert budget.order_status == 'converted'
        assert order.items.count() == 1
