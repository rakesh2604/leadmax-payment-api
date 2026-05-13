from decimal import Decimal
from rest_framework import serializers

from .models import Transaction


class PaymentRequestSerializer(serializers.Serializer):
    sender_account_id = serializers.IntegerField()
    receiver_account_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))

    def validate(self, data):
        if data['sender_account_id'] == data['receiver_account_id']:
            raise serializers.ValidationError('Sender and receiver must be different accounts.')
        return data


class TransactionSerializer(serializers.ModelSerializer):
    sender_account_number = serializers.CharField(source='sender_account.account_number', read_only=True)
    receiver_account_number = serializers.CharField(source='receiver_account.account_number', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'sender_account_id',
            'receiver_account_id',
            'sender_account_number',
            'receiver_account_number',
            'amount',
            'status',
            'created_at',
        ]
