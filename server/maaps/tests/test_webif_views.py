from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import maaps.models as models


class WebifViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create required prices for space rent
        models.Price.objects.create(
            identifier='spaceRentPayment.monthly',
            default=50.0,
            members=30.0
        )
        models.Price.objects.create(
            identifier='spaceRentPayment.daily',
            default=10.0,
            members=5.0
        )

        # Admin user
        self.admin = User.objects.create_user(
            username='admin.webif',
            first_name='Admin',
            last_name='Webif',
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
        self.admin.set_password('adminpass')
        self.admin.save()

        # Regular user
        self.user = User.objects.create_user(
            username='webif.user',
            first_name='Webif',
            last_name='User',
            email='webif@example.com'
        )
        self.user.profile.prepaid_deposit = 100.0
        self.user.profile.save()

    def test_webif_requires_login(self):
        """Test that webif URLs redirect to login for unauthenticated users."""
        response = self.client.get("/webif/")
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_webif_dashboard_authenticated(self):
        """Test webif dashboard access for authenticated staff."""
        self.client.force_login(self.admin)
        response = self.client.get("/webif/")
        self.assertEqual(response.status_code, 200)

    def test_webif_info_page(self):
        """Test webif info page renders."""
        self.client.force_login(self.admin)
        response = self.client.get("/webif/info")
        self.assertEqual(response.status_code, 200)

    def test_webif_user_list(self):
        """Test user list page."""
        self.client.force_login(self.admin)
        response = self.client.get("/webif/user/list")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Benutzer')

    def test_webif_user_show(self):
        """Test user show page."""
        self.client.force_login(self.admin)
        response = self.client.get(f"/webif/user/show/{self.user.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Webif')

    def test_webif_user_create(self):
        """Test creating a user via webif."""
        self.client.force_login(self.admin)
        post_data = {
            'username': 'new.created',
            'first_name': 'New',
            'last_name': 'Created',
            'email': 'new@example.com',
            'prepaid_deposit': '0',
            'street': '', 'postalcode': '', 'city': '',
        }
        response = self.client.post("/webif/user/create", post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after create

        user = User.objects.get(username='new.created')
        self.assertEqual(user.email, 'new@example.com')

    def test_webif_user_update(self):
        """Test updating user profile."""
        self.client.force_login(self.admin)
        post_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'webif@example.com',
            'company_name': 'New Company',
            'street': 'Teststr. 1',
            'postalcode': '12345',
            'city': 'Teststadt',
            'prepaid_deposit': '0',
            'monthly_payment': 'on',
            'commercial_account': '',
            'discount_account': '',
            'allow_postpaid': '',
        }
        response = self.client.post(f"/webif/user/update/{self.user.id}", post_data)
        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.profile.company_name, 'New Company')
        self.assertTrue(self.user.profile.monthly_payment)

    def test_webif_user_delete(self):
        """Test deleting a user via webif - profile is deleted, user remains."""
        self.client.force_login(self.admin)
        user_to_delete = User.objects.create_user(
            username='to.delete', email='delete@example.com'
        )
        # Delete should redirect
        response = self.client.post(f"/webif/user/delete/{user_to_delete.id}")
        self.assertEqual(response.status_code, 302)
        # Note: The view deletes the Profile, not the User (catches exception)
        # Verify profile is gone
        self.assertFalse(models.Profile.objects.filter(id=user_to_delete.id).exists())

    def test_webif_user_deposit(self):
        """Test user deposit page (GET) and POST for cash deposit."""
        self.client.force_login(self.admin)

        # GET should render deposit form
        response = self.client.get(f"/webif/user/deposit/{self.user.profile.id}")
        self.assertEqual(response.status_code, 200)

        # POST cash deposit
        response = self.client.post(f"/webif/user/deposit/{self.user.profile.id}", {
            'deposit_value': '25.0',
            'type': models.TransactionType.from_cash_for_deposit
        })
        self.assertEqual(response.status_code, 302)  # Redirect to invoice

        # Verify transaction and deposit were created
        tx = models.Transaction.objects.filter(
            user=self.user,
            type=models.TransactionType.from_cash_for_deposit
        ).first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.value, 25.0)

    def test_webif_prices_page(self):
        """Test prices page renders."""
        self.client.force_login(self.admin)
        response = self.client.get("/webif/prices")
        self.assertEqual(response.status_code, 200)

    def test_webif_agb_page(self):
        """Test AGB page renders."""
        self.client.force_login(self.admin)
        response = self.client.get("/webif/agb")
        self.assertEqual(response.status_code, 200)

    def test_webif_contract_page(self):
        """Test contract page renders."""
        self.client.force_login(self.admin)
        response = self.client.get("/webif/contract")
        self.assertEqual(response.status_code, 200)

    def test_webif_contract_paypal_page(self):
        """Test contract paypal page renders."""
        self.client.force_login(self.admin)
        response = self.client.get("/webif/contract_paypal")
        self.assertEqual(response.status_code, 200)

    def test_webif_user_contract(self):
        """Test user contract page renders."""
        self.client.force_login(self.admin)
        response = self.client.get(f"/webif/user/contract/{self.user.id}")
        self.assertEqual(response.status_code, 200)

    def test_webif_user_contract_sepa(self):
        """Test user contract SEPA page renders."""
        self.client.force_login(self.admin)
        response = self.client.get(f"/webif/user/contract_sepa/{self.user.id}")
        self.assertEqual(response.status_code, 200)

    def test_webif_user_contract_paypal(self):
        """Test user contract paypal page renders."""
        self.client.force_login(self.admin)
        response = self.client.get(f"/webif/user/contract_paypal/{self.user.id}")
        self.assertEqual(response.status_code, 200)

    def test_webif_user_create_new_card(self):
        """Test creating new RFID card for user - redirects to user show."""
        self.client.force_login(self.admin)
        response = self.client.post(f"/webif/user/create_new_card/{self.user.id}", {
            'token_value': 'U:newcard;uuid123'
        })
        # View redirects after creating token
        self.assertEqual(response.status_code, 302)

        # Verify new token was created
        tokens = models.Token.objects.filter(profile=self.user.profile, enabled=True)
        self.assertTrue(tokens.exists())

    def test_webif_invoice_list(self):
        """Test invoice list page."""
        self.client.force_login(self.admin)
        response = self.client.get("/webif/invoice/list")
        self.assertEqual(response.status_code, 200)

    def test_webif_invoice_show(self):
        """Test invoice show page."""
        self.client.force_login(self.admin)
        # Create an invoice first
        tx = models.Transaction.objects.create(
            user=self.user,
            value=25.0,
            type=models.TransactionType.from_cash_for_deposit
        )
        invoice = models.Invoice.objects.create(
            user=self.user,
            value=25.0,
            total=25.0,
            transaction=tx
        )

        response = self.client.get(f"/webif/invoice/show/{invoice.id}")
        self.assertEqual(response.status_code, 200)

    def test_webif_invoice_list_createable(self):
        """Test list of invoices that can be created."""
        self.client.force_login(self.admin)
        response = self.client.get("/webif/invoice/list_createable")
        self.assertEqual(response.status_code, 200)

    def test_webif_invoice_create_postpaid(self):
        """Test creating an invoice for a postpaid user."""
        # Enable postpaid for user
        self.user.profile.allow_postpaid = True
        self.user.profile.save()

        self.client.force_login(self.admin)
        # Create an unpayed material payment
        material = models.MaterialPayment.objects.create(
            user=self.user,
            creator=self.admin,
            price=15.0
        )

        response = self.client.post(f"/webif/invoice/create/{self.user.id}", {
            'unpayed_materials': [str(material.id)]
        })
        self.assertEqual(response.status_code, 302)  # Redirect to invoice show

        invoice = models.Invoice.objects.filter(user=self.user).first()
        self.assertIsNotNone(invoice)
        material.refresh_from_db()
        self.assertEqual(material.invoice, invoice)

    def test_webif_invoice_create_regular(self):
        """Test creating an invoice for a regular (non-postpaid) user."""
        self.client.force_login(self.admin)
        # Create an unpayed space rent payment
        spacerent = models.SpaceRentPayment.objects.create(
            user=self.user,
            for_user=self.user,
            price=50.0,
            type=models.SpaceRentPaymentType.monthly
        )

        response = self.client.post(f"/webif/invoice/create/{self.user.id}", {
            'spaceRentPayments': [str(spacerent.id)]
        })
        self.assertEqual(response.status_code, 302)  # Redirect to invoice show

        invoice = models.Invoice.objects.filter(user=self.user).first()
        self.assertIsNotNone(invoice)
        spacerent.refresh_from_db()
        self.assertEqual(spacerent.invoice, invoice)
        self.assertEqual(invoice.value, 50.0)

    def test_webif_session_end(self):
        """Test manual session end from webif."""
        self.client.force_login(self.admin)
        # Create a machine and session
        machine = models.Machine.objects.create(name='Test Machine')
        session = models.MachineSession.objects.create(
            machine=machine,
            user=self.user,
            start=timezone.now()
        )

        response = self.client.post(f"/webif/session/end/{session.id}")
        self.assertEqual(response.status_code, 302)

        session.refresh_from_db()
        self.assertIsNotNone(session.end)

    def test_webif_space_access_end(self):
        """Test space access tracking end."""
        self.client.force_login(self.admin)
        tracking = models.SpaceAccessTracking.objects.create(
            user=self.user
        )
        response = self.client.post(f"/webif/spaceaccesstracking/end/{tracking.id}")
        self.assertEqual(response.status_code, 302)

        tracking.refresh_from_db()
        self.assertIsNotNone(tracking.end)