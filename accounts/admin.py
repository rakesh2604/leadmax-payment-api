from django.contrib import admin
from .models import BankAccount


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'account_name', 'user', 'balance', 'created_at']
    search_fields = ['account_name', 'user__email']
