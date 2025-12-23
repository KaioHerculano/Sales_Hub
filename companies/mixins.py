from django.core.exceptions import PermissionDenied
from django.contrib import messages


class CompanyObjectMixin:

    def get_queryset(self):
        queryset = super().get_queryset()
        try:
            return queryset.filter(company=self.request.user.profile.company)
        except AttributeError:
            messages.error(self.request, "Seu usuário não está vinculado a nenhuma empresa.")
            raise PermissionDenied("Usuário não associado a uma empresa.")