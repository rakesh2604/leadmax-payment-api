from django.contrib import admin
from .models import BankAccount


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'bank_name', 'account_name', 'account_number', 'user', 'balance', 'created_at']
    search_fields = ['account_name', 'account_number', 'bank_name', 'user__email']
