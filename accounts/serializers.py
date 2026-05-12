from decimal import Decimal
from rest_framework import serializers
from .models import BankAccount


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'account_name', 'balance', 'created_at']
        read_only_fields = ['id', 'balance', 'created_at']


class TopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
