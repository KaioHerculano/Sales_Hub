import pytest
from django.urls import reverse
from sales.models import Sale
from model_bakery import baker

@pytest.mark.django_db
class TestSalesViews:
    def test_sale_list_view(self, auth_client, company):
        baker.make(Sale, company=company, order_status='finalized')
        url = reverse('sale_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_invoice_pdf_view(self, auth_client, company):
        from clients.models import Client
        client = baker.make(Client, company=company, telephone='65999999999')
        sale = baker.make(Sale, company=company, client=client)
        url = reverse('sale_invoice', kwargs={'pk': sale.pk})
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'

    def test_get_product_price_api(self, auth_client, company):
        from products.models import Product
        product = baker.make(Product, company=company, selling_price=150.75)
        url = reverse('get_product_price')
        response = auth_client.get(f"{url}?product_id={product.id}")
        assert response.status_code == 200
        assert response.json()['price'] == '150.75'

    def test_sale_create_post_with_items(self, auth_client, company):
        from products.models import Product
        from clients.models import Client
        product = baker.make(Product, company=company, quantity=10, selling_price=100.00)
        client = baker.make(Client, company=company, telephone='65999999999')
        
        url = reverse('sale_create')
        data = {
            'client': client.id,
            'discount': 10,
            'payment_method': 'cash',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-product': product.id,
            'items-0-quantity': '1',
            'items-0-unit_price': '100.00',
        }
        # Note: SaleItemFormSet in SaleCreateView doesn't have a prefix by default in the template but use 'items' in code?
        # Let's check sales/views.py line 59: context['items'] = forms.SaleItemFormSet(...)
        # Wait, if no prefix is passed, it uses the default.
        response = auth_client.post(url, data)
        # If it fails, I'll check the prefix.
        assert response.status_code == 302
