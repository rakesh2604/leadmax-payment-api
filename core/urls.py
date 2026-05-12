from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'users':    'http://127.0.0.1:8000/api/users/',
        'login':    'http://127.0.0.1:8000/api/auth/login/',
        'refresh':  'http://127.0.0.1:8000/api/auth/refresh/',
        'accounts': 'http://127.0.0.1:8000/api/accounts/',
        'payments': 'http://127.0.0.1:8000/api/payments/',
        'history':  'http://127.0.0.1:8000/api/payments/history/',
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),

    path('api/users/', include('users.urls')),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/accounts/', include('accounts.urls')),
    path('api/payments/', include('payments.urls')),
]
