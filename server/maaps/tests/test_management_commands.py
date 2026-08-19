from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from io import StringIO
from django.utils import timezone
from datetime import timedelta
import maaps.models as models


class ManagementCommandsTestCase(TestCase):
    def setUp(self):
        # Create required prices
        models.Price.objects.create(
            identifier='spaceRentPayment.monthly',
            default=50.0,
            members=30.0
        )

        self.user = User.objects.create_user(
            username='monthly.member',
            first_name='Monthly',
            last_name='Member',
            email='monthly@example.com'
        )
        self.user.profile.monthly_payment = True
        self.user.profile.prepaid_deposit = 200.0
        self.user.profile.save()

    def test_create_old_invoices_creates_invoices(self):
        """Test management command creates invoices from old transactions."""
        # Create transactions with 'from_cash_for_deposit' type (what command expects)
        tx = models.Transaction.objects.create(
            user=self.user,
            value=25.0,
            type='from_cash_for_deposit'
        )

        out = StringIO()
        call_command('create_old_invoices', stdout=out)

        invoices = models.Invoice.objects.filter(user=self.user)
        self.assertTrue(invoices.exists())
        invoice = invoices.first()
        self.assertEqual(invoice.transaction, tx)
        self.assertEqual(invoice.value, 25.0)
