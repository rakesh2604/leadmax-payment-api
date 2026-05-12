from django.urls import path
from .views import BankAccountListCreateView, BankAccountDetailView, TopUpView

urlpatterns = [
    path('', BankAccountListCreateView.as_view(), name='account-list-create'),
    path('<int:pk>/', BankAccountDetailView.as_view(), name='account-detail'),
    path('<int:pk>/topup/', TopUpView.as_view(), name='account-topup'),
]
