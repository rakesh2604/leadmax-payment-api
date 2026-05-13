from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .auth_views import LoginView, RefreshView


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    base = request.build_absolute_uri('/').rstrip('/')
    return Response({
        'users': f'{base}/api/users/',
        'login': f'{base}/api/auth/login/',
        'refresh': f'{base}/api/auth/refresh/',
        'accounts': f'{base}/api/accounts/',
        'payments': f'{base}/api/payments/',
        'history': f'{base}/api/payments/history/',
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),

    path('api/users/', include('users.urls')),
    path('api/auth/login/', LoginView.as_view(), name='token-obtain'),
    path('api/auth/refresh/', RefreshView.as_view(), name='token-refresh'),
    path('api/accounts/', include('accounts.urls')),
    path('api/payments/', include('payments.urls')),
]
