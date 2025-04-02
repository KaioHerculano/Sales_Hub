from django.contrib import admin
from .models import Client


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth', 'address', 'neighborhood', 'complement', 'telephone', 'email', 'cpf', 'rg')
    search_fields = ('name', 'address', 'neighborhood')


admin.site.register(Client, ClientAdmin)
