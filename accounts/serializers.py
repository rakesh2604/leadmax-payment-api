from decimal import Decimal
from rest_framework import serializers

from .models import BankAccount


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'bank_name', 'account_name', 'account_number', 'balance', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'balance': {
                'required': False,
                'min_value': Decimal('0'),
            },
        }


class TopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
