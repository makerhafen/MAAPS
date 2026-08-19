from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import maaps.models as models


class ModelTestCase(TestCase):
    def setUp(self):
        # Create standard test user
        self.user = User.objects.create_user(
            username='john.doe',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='secretpassword'
        )
        self.profile = self.user.profile
        self.profile.prepaid_deposit = 100.00
        self.profile.save()

        # Create prices
        self.price_per_usage = models.Price.objects.create(
            identifier='Usage Price',
            default=5.0,
            members=2.0,
            commercial=10.0
        )
        self.price_per_hour = models.Price.objects.create(
            identifier='Hour Price',
            default=10.0,
            members=5.0,
            commercial=20.0
        )

        # Create machine
        self.machine = models.Machine.objects.create(
            name='3D Printer 1',
            price_per_usage=self.price_per_usage,
            price_per_hour=self.price_per_hour,
            tutor_required_count=1
        )

        # Create machine token
        self.machine_token = models.Token.objects.create(
            identifier='M:3DPrinter1;uuid123',
            machine=self.machine,
            can_write=True
        )

    def test_user_profile_signal_creation(self):
        """Test that profile and token are automatically created on User save via signal."""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)
        # Token should be created automatically
        tokens = models.Token.objects.filter(profile=self.profile)
        self.assertTrue(tokens.exists())
        user_token = tokens.first()
        self.assertTrue(user_token.identifier.startswith(f"U:{self.user.username};"))
        self.assertTrue(user_token.can_write)

    def test_machine_allowed_users(self):
        """Test machine permissions for allowed users."""
        self.machine.allowed_users.add(self.user)
        self.assertTrue(self.machine.user_is_allowed(self.user))

        other_user = User.objects.create_user(username='other.user', email='other@example.com')
        self.assertFalse(self.machine.user_is_allowed(other_user))

    def test_machine_tutor_requirement(self):
        """Test machine tutor requirement logic based on session history."""
        # Machine requires 1 tutor session
        self.assertTrue(self.machine.user_requires_tutor(self.user))

        # Create a session with tutor
        tutor_user = User.objects.create_user(username='tutor.user', email='tutor@example.com')
        models.MachineSession.objects.create(
            machine=self.machine,
            user=self.user,
            tutor=tutor_user,
            start=timezone.now() - timedelta(hours=2),
            end=timezone.now() - timedelta(hours=1)
        )

        # Now user has 1 tutored session, so tutor should no longer be required
        self.assertFalse(self.machine.user_requires_tutor(self.user))

    def test_machine_payment_requirement(self):
        """Test if payment is required based on profile settings."""
        self.profile.monthly_payment = False
        self.profile.save()
        self.assertTrue(self.machine.requires_payment(self.profile))

        # Price calculation check
        p_usage, p_hour = self.machine.get_price(self.profile)
        self.assertEqual(p_usage, 5.0)
        self.assertEqual(p_hour, 10.0)

    def test_space_access_tracking(self):
        """Test space access tracking model."""
        tracking = models.SpaceAccessTracking.objects.create(
            user=self.user,
            start=timezone.now()
        )
        self.assertIsNone(tracking.end)
        tracking.end = timezone.now() + timedelta(hours=3)
        tracking.save()
        self.assertIsNotNone(tracking.end)

    def test_transaction_and_invoicing(self):
        """Test creating deposits and transactions."""
        deposit = models.PrepaidDepositPayment.objects.create(
            user=self.user,
            price=25.0
        )
        self.assertEqual(deposit.price, 25.0)

        tx = models.Transaction.objects.create(
            user=self.user,
            value=25.0,
            type=models.TransactionType.from_cash_for_deposit
        )
        self.assertEqual(tx.user, self.user)
