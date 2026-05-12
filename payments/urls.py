from django.urls import path
from .views import PaymentView, TransactionHistoryView

urlpatterns = [
    path('', PaymentView.as_view(), name='payment'),
    path('history/', TransactionHistoryView.as_view(), name='transaction-history'),
]
