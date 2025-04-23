import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from . import metrics
from companies.models import Company

@login_required(login_url='login')
def home(request):
    Company = request.user.profile.company

    product_metrics = metrics.get_product_metrics(Company)
    sales_metrics = metrics.get_sales_metrics(Company)
    daily_sales_data = metrics.get_daily_sales_data(Company)
    daily_sales_quantity_data = metrics.get_daily_sales_quantity_data(Company)
    product_count_by_category_metric = metrics.get_product_count_by_category_metric(Company)
    graphic_product_brand_metric = metrics.get_graphic_product_brand_metric(Company)


    seller_metrics = metrics.get_sales_by_seller_metrics(Company)
    top_clients_data = metrics.get_top_clients_last_month(Company)

    context = {
        'product_metrics': product_metrics,
        'sales_metrics': sales_metrics,
        'daily_sales_data': json.dumps(daily_sales_data),
        'daily_sales_quantity_data': json.dumps(daily_sales_quantity_data),
        'product_count_by_category': json.dumps(product_count_by_category_metric),
        'product_count_by_brand': json.dumps(graphic_product_brand_metric),
        'value_by_seller': json.dumps(seller_metrics['value_by_seller']),
        'top_clients': json.dumps(top_clients_data),
        'sales_by_seller_data': json.dumps({
            'sellers': list(seller_metrics['value_by_seller'].keys()),
            'values': list(seller_metrics['value_by_seller'].values()),
        }),
        'top_customers_data': json.dumps({
            'clients': list(top_clients_data['clients']),
            'total_values': list(top_clients_data['values']),
        }),
    }

    return render(request, 'home.html', context)



