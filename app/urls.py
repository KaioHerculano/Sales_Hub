from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('api/v1/', include('authentication.urls')),

    path('', views.home, name='home'),
    path('', include('brands.urls')),
    path('', include('budgets.urls')),
    path('', include('categories.urls')),
    path('', include('clients.urls')),
    path('', include('suppliers.urls')),
    path('', include('inflows.urls')),
    path('', include('outflows.urls')),
    path('', include('products.urls')),
    path('', include('stockmoviment.urls')),
    path('', include('sales.urls')),
    path('', include('sale_order.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
