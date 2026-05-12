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

        # Resolve sender — must belong to the authenticated user
        try:
            sender = BankAccount.objects.get(pk=sender_id, user=request.user)
        except BankAccount.DoesNotExist:
            return Response(
                {'error': 'Sender account not found or does not belong to you.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Resolve receiver — can be any valid account in the system
        try:
            receiver = BankAccount.objects.get(pk=receiver_id)
        except BankAccount.DoesNotExist:
            txn = Transaction.objects.create(
                sender_account=sender,
                receiver_account=sender,  # placeholder; receiver invalid
                amount=amount,
                status=Transaction.STATUS_FAILED,
            )
            return Response(
                {'error': 'Receiver account not found.', 'transaction_id': txn.id, 'status': 'FAILED'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Insufficient balance → log a FAILED transaction and return
        if sender.balance < amount:
            txn = Transaction.objects.create(
                sender_account=sender,
                receiver_account=receiver,
                amount=amount,
                status=Transaction.STATUS_FAILED,
            )
            return Response(
                {
                    'error': 'Insufficient balance.',
                    'transaction_id': txn.id,
                    'status': 'FAILED',
                    'available_balance': str(sender.balance),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Atomic transfer — deduct then credit so both succeed or neither does
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
                'message': 'Payment successful.',
                'transaction_id': txn.id,
                'status': 'SUCCESS',
                'sender_balance': str(sender.balance),
            },
            status=status.HTTP_201_CREATED,
        )


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Return all transactions where the user is either the sender or receiver
        user_accounts = BankAccount.objects.filter(user=request.user).values_list('id', flat=True)
        transactions = Transaction.objects.filter(
            Q(sender_account__in=user_accounts) | Q(receiver_account__in=user_accounts)
        ).order_by('-created_at')

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
