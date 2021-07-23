from django.core.management.base import BaseCommand, CommandError
from maaps.models import Transaction, Invoice, PrepaidDepositPayment

class Command(BaseCommand):
    help = 'fix old invoices and transactions'


    def handle(self, *args, **options):

        transactions = Transaction.objects.filter(type="from_cash_for_deposit", invoice=None)
        print(len(transactions))
        for transaction in transactions:
            invoice = Invoice()
            invoice.created = transaction.created
            invoice.updated = transaction.updated
            invoice.type = "receipt"
            invoice.transaction = transaction
            invoice.due = transaction.created
            invoice.value = transaction.value
            invoice.total = transaction.value
            invoice.user = transaction.user
            invoice.save()

            payment = PrepaidDepositPayment()
            payment.invoice = invoice
            payment.created = transaction.created
            payment.updated = transaction.updated
            payment.price = transaction.value
            payment.user = transaction.user
            payment.save()