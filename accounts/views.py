from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import BankAccount
from .serializers import BankAccountSerializer, TopUpSerializer

MAX_ACCOUNTS_PER_USER = 3


class BankAccountListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = BankAccount.objects.filter(user=request.user)
        serializer = BankAccountSerializer(accounts, many=True)
        return Response(serializer.data)

    def post(self, request):
        existing_count = BankAccount.objects.filter(user=request.user).count()
        if existing_count >= MAX_ACCOUNTS_PER_USER:
            return Response(
                {
                    'detail': (
                        f'Account limit reached ({MAX_ACCOUNTS_PER_USER} accounts per user). '
                        'Close or remove an account before adding another.'
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BankAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BankAccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return BankAccount.objects.get(pk=pk, user=user)
        except BankAccount.DoesNotExist:
            return None

    def delete(self, request, pk):
        account = self.get_object(pk, request.user)
        if not account:
            return Response(
                {'detail': 'No bank account found for this id on your profile.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TopUpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            account = BankAccount.objects.get(pk=pk, user=request.user)
        except BankAccount.DoesNotExist:
            return Response(
                {'detail': 'No bank account found for this id on your profile.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TopUpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        account.balance += serializer.validated_data['amount']
        account.save()
        return Response(
            {
                'detail': 'Top-up completed.',
                'new_balance': str(account.balance),
            },
            status=status.HTTP_200_OK,
        )
