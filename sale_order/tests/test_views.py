import pytest
from django.urls import reverse
from sales.models import Sale
from model_bakery import baker

@pytest.mark.django_db
class TestOrderViews:
    def test_order_list_view(self, auth_client, company):
        baker.make(Sale, company=company, sale_type='order', order_status='finalized')
        url = reverse('order_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_order_pdf_view(self, auth_client, company):
        # Need a client for PDF generation as discovered in sales tests
        from clients.models import Client
        client = baker.make(Client, company=company, telephone='65999999999')
        order = baker.make(Sale, company=company, sale_type='order', client=client)
        url = reverse('order_pdf', kwargs={'pk': order.pk})
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'

    def test_order_detail_view(self, auth_client, company):
        order = baker.make(Sale, company=company, sale_type='order')
        url = reverse('order_detail', kwargs={'pk': order.pk})
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_order_create_post_with_items(self, auth_client, company):
        from products.models import Product
        from clients.models import Client
        product = baker.make(Product, company=company, quantity=10, selling_price=100.00)
        client = baker.make(Client, company=company, telephone='65999999999')
        
        url = reverse('order_create')
        data = {
            'client': client.id,
            'discount': 0,
            'order_status': 'finalized',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-product': product.id,
            'items-0-quantity': '2',
            'items-0-unit_price': '100.00',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 302
        
        # Check stock decrease
        product.refresh_from_db()
        assert product.quantity == 8
        
        # Check sale total
        sale = Sale.objects.filter(client=client).last()
        assert sale.total == 200.00
