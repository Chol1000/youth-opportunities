from django.http import JsonResponse
from django.views import View
import logging

logger = logging.getLogger(__name__)

class LoggingView(View):
    def dispatch(self, request, *args, **kwargs):
        print(f'INFO "{request.method} {request.get_full_path()} HTTP/1.1"', flush=True)
        return super().dispatch(request, *args, **kwargs)
