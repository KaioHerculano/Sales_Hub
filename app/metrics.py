from django.db.models import Sum, F
from django.utils import timezone
from django.utils.formats import number_format
from brands.models import Brand
from categories.models import Category
from products.models import Product
from outflows.models import Outflow
from sales.models import Sale


def get_product_metrics():
    products = Product.objects.all()
    total_cost_price = sum(product.cost_price * product.quantity for product in products)
    total_selling_price = sum(product.selling_price * product.quantity for product in products)
    total_quantity = sum(product.quantity for product in products)
    total_profit = total_selling_price - total_cost_price

    return dict(
        total_cost_price = number_format(total_cost_price, decimal_pos=2, force_grouping=True),
        total_selling_price = number_format(total_selling_price, decimal_pos=2, force_grouping=True),
        total_quantity = total_quantity,
        total_profit = number_format(total_profit, decimal_pos=2, force_grouping=True),
    )

def get_sales_metrics():
    total_sales = Sale.objects.count()
    total_sales_value = 0
    total_sales_profit = 0
    total_products_sold = 0

    for sale in Sale.objects.all():
        total_sales_value += sale.total

        sale_cost = sum(item.quantity * item.purchase_price for item in sale.items.all())
        sale_profit = sale.total - sale_cost
        total_sales_profit += sale_profit

        total_products_sold += sum(item.quantity for item in sale.items.all())

    return dict(
        total_sales=total_sales,
        total_sales_value=number_format(total_sales_value, decimal_pos=2, force_grouping=True),
        total_sales_profit=number_format(total_sales_profit, decimal_pos=2, force_grouping=True),
        total_products_sold=total_products_sold,
    )

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
