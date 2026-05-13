from django.db import transaction as db_transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.models import BankAccount
from .models import Transaction
from .serializers import PaymentRequestSerializer, TransactionSerializer


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        sender_id = data['sender_account_id']
        receiver_id = data['receiver_account_id']
        amount = data['amount']

        try:
            sender = BankAccount.objects.get(pk=sender_id, user=request.user)
        except BankAccount.DoesNotExist:
            return Response(
                {'detail': 'Sender account was not found or is not linked to your user.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            receiver = BankAccount.objects.get(pk=receiver_id)
        except BankAccount.DoesNotExist:
            return Response(
                {'detail': 'Receiver account was not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if sender.balance < amount:
            with db_transaction.atomic():
                txn = Transaction.objects.create(
                    sender_account=sender,
                    receiver_account=receiver,
                    amount=amount,
                    status=Transaction.STATUS_FAILED,
                )
            return Response(
                {
                    'detail': 'Insufficient balance for this transfer.',
                    'transaction_id': txn.id,
                    'status': Transaction.STATUS_FAILED,
                    'available_balance': str(sender.balance),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with db_transaction.atomic():
            sender.balance -= amount
            sender.save()
            receiver.balance += amount
            receiver.save()

            txn = Transaction.objects.create(
                sender_account=sender,
                receiver_account=receiver,
                amount=amount,
                status=Transaction.STATUS_SUCCESS,
            )

        return Response(
            {
                'detail': 'Payment completed successfully.',
                'transaction_id': txn.id,
                'status': Transaction.STATUS_SUCCESS,
                'sender_balance': str(sender.balance),
            },
            status=status.HTTP_201_CREATED,
        )


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_accounts = BankAccount.objects.filter(user=request.user).values_list('id', flat=True)
        transactions = Transaction.objects.filter(
            Q(sender_account__in=user_accounts) | Q(receiver_account__in=user_accounts)
        ).order_by('-created_at')

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
