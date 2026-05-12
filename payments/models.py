from django.db import models


class Transaction(models.Model):
    STATUS_SUCCESS = 'SUCCESS'
    STATUS_FAILED = 'FAILED'
    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
    ]

    sender_account = models.ForeignKey(
        'accounts.BankAccount',
        on_delete=models.CASCADE,
        related_name='sent_transactions',
    )
    receiver_account = models.ForeignKey(
        'accounts.BankAccount',
        on_delete=models.CASCADE,
        related_name='received_transactions',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Txn #{self.id} | {self.sender_account} → {self.receiver_account} | {self.amount} | {self.status}"
