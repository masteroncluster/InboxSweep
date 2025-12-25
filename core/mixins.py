from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class AuthRequiredMixin(LoginRequiredMixin):
    """Custom authentication mixin with redirect to login"""
    login_url = '/accounts/login/'
    redirect_field_name = 'next'


class AjaxResponseMixin:
    """Mixin for JSON responses"""
    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)


class CsrfExemptMixin:
    """Mixin to exempt CSRF protection"""
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)