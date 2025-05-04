from django.contrib import admin
from companies.models import Company, UserProfile
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id', 'is_active', 'email')
    search_fields = ('name', 'tax_id', 'email')
    list_filter = ('is_active',)

    def get_group(self, obj):
        return f"Empresa: {obj.name}"
    get_group.short_description = "Grupo Associado"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'is_company_admin')
    search_fields = ('user__username', 'company__name')
    list_filter = ('company', 'is_company_admin')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.user.groups.all()])
    get_groups.short_description = "Grupos do Usuário"

class CustomGroupAdmin(GroupAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(name__startswith="Empresa:")

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)