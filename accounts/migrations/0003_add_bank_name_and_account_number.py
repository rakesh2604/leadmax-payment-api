import uuid

from django.db import migrations, models


def assign_bank_fields(apps, schema_editor):
    BankAccount = apps.get_model('accounts', 'BankAccount')
    for acc in BankAccount.objects.all():
        if not acc.bank_name:
            acc.bank_name = 'Unspecified'
        if not acc.account_number:
            acc.account_number = f'A{acc.pk}-{uuid.uuid4().hex}'[:32]
        acc.save(update_fields=['bank_name', 'account_number'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankaccount',
            name='bank_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='bankaccount',
            name='account_number',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.RunPython(assign_bank_fields, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='account_number',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
