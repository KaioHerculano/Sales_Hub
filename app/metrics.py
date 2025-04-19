from django.db.models import Sum, F, Q
from django.utils import timezone
from django.utils.formats import number_format
from brands.models import Brand
from categories.models import Category
from products.models import Product
from outflows.models import Outflow
from sales.models import Sale
from django.utils.timezone import now, timedelta
from collections import defaultdict
from decimal import Decimal


def get_product_metrics():
    products = Product.objects.filter(quantity__gt=0)
    total_cost_price = sum(product.cost_price * product.quantity for product in products)
    total_selling_price = sum(product.selling_price * product.quantity for product in products)
    total_quantity = sum(product.quantity for product in products)
    total_profit = total_selling_price - total_cost_price


    return dict(
        total_cost_price=number_format(total_cost_price, decimal_pos=2, force_grouping=True),
        total_selling_price=number_format(total_selling_price, decimal_pos=2, force_grouping=True),
        total_quantity=total_quantity,
        total_profit=number_format(total_profit, decimal_pos=2, force_grouping=True),
    )



def get_sales_metrics():
    sales = Sale.objects.filter(
        Q(sale_type__in=['quote', 'order']) &
        Q(order_status='finalized')
    )
    
    outflows = Outflow.objects.exclude(
        sale_reference__startswith='Venda '
    )
    
    total_sales_count = sales.count()
    total_sales_value = Decimal('0')
    total_sales_profit = Decimal('0')
    total_products_sold = 0
    
    for sale in sales:
        total_sales_value += sale.total
        sale_cost = sum(item.quantity * item.purchase_price for item in sale.items.all())
        total_sales_profit += sale.total - sale_cost
        total_products_sold += sum(item.quantity for item in sale.items.all())
    
    for outflow in outflows:
        outflow_value = outflow.product.selling_price * outflow.quantity
        outflow_cost = outflow.product.cost_price * outflow.quantity
        
        total_sales_value += outflow_value
        total_sales_profit += outflow_value - outflow_cost
        total_products_sold += outflow.quantity
    
    return {
        'total_sales': total_sales_count,
        'total_outflows': outflows.count(),
        'total_sales_value': number_format(total_sales_value, decimal_pos=2, force_grouping=True),
        'total_sales_profit': number_format(total_sales_profit, decimal_pos=2, force_grouping=True),
        'total_products_sold': total_products_sold,
    }


def get_daily_sales_data():
    today = timezone.now().date()
    dates = [str(today - timezone.timedelta(days=i)) for i in range(6, -1, -1)]
    values = list()

    for date in dates:
        sales_total = Outflow.objects.filter(
            created_at__date=date
        ).aggregate(
            total_sales=Sum(F('product__selling_price') * F('quantity'))
        )['total_sales'] or 0
        values.append(float(sales_total))

    return dict(
        dates=dates,
        values=values,
    )


def get_daily_sales_quantity_data():
    today = timezone.now().date()
    dates = [str(today - timezone.timedelta(days=i)) for i in range(6, -1, -1)]
    quantities = list()

    for date in dates:
        sales_quantity = Outflow.objects.filter(created_at__date=date).count()
        quantities.append(sales_quantity)

    return dict(
        dates=dates,
        values=quantities,
    )


def get_product_count_by_category_metric():
    categories = Category.objects.all()
    return {category.name: Product.objects.filter(category=category).count() for category in categories}


def get_graphic_product_brand_metric():
    brands = Brand.objects.all()
    return {brand.name: Product.objects.filter(brand=brand).count() for brand in brands}


def get_sales_by_seller_metrics():
    today = now().date()
    start_of_month = today.replace(day=1)
    sales = Sale.objects.filter(
        sale_type__in=['quote', 'order'],
        order_status='finalized',
        sale_date__gte=start_of_month
    )

    value_by_seller = defaultdict(float)

    for sale in sales:
        if sale.seller:
            seller_name = sale.seller.get_full_name() or sale.seller.username
            value_by_seller[seller_name] += float(sale.total)

    return {
        'value_by_seller': value_by_seller
    }

def get_top_clients_last_month():
    today = now().date()
    last_month = today - timedelta(days=30)

    sales = Sale.objects.filter(
        sale_type__in=['quote', 'order'],
        order_status='finalized',
        sale_date__gte=last_month
    )

    clients_total = defaultdict(Decimal)

    for sale in sales:
        if sale.client:
            client_name = str(sale.client)
            try:
                total_value = sale.total if isinstance(sale.total, Decimal) else Decimal(sale.total)
                clients_total[client_name] += total_value
            except (ValueError, TypeError) as e:
                continue

    sorted_clients = sorted(clients_total.items(), key=lambda x: x[1], reverse=True)[:3]
    return {
        'clients': [client for client, _ in sorted_clients],
        'values': [float(value) for _, value in sorted_clients]
    }