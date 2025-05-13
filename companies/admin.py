from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from companies.models import Company, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil do Usuário'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


class UserProfileCompanyInline(admin.TabularInline):
    model = UserProfile
    extra = 1
    fields = ('user', 'is_company_admin')
    can_delete = True
    show_change_link = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class CustomFormSet(formset):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for form in self.forms:
                    if not form.instance.pk:
                        form.fields['user'].queryset = User.objects.filter(profile__company__isnull=True)

        return CustomFormSet




@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'chpj', 'is_active', 'email')
    search_fields = ('name', 'chpj', 'email')
    list_filter = ('is_active',)
    inlines = [UserProfileCompanyInline]

    def get_group(self, obj):
        return f"Empresa: {obj.name}"
    get_group.short_description = "Grupo Associado"

"""
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'is_company_admin')
    search_fields = ('user__username', 'company__name')
    list_filter = ('company', 'is_company_admin')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.user.groups.all()])
    get_groups.short_description = "Grupos do Usuário"
"""


class CustomGroupAdmin(GroupAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(name__startswith="Empresa:")

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
