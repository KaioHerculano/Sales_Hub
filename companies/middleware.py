from django.http import Http404


class CompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            request.company = request.user.profile.company
        response = self.get_response(request)
        return response