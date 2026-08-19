from django.test import TestCase, Client
from django.contrib.auth.models import User
import maaps.models as models


class PosViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Staff user for POS
        self.staff = User.objects.create_user(
            username='pos.staff',
            first_name='POS',
            last_name='Staff',
            email='staff@example.com'
        )
        self.staff.is_staff = True
        self.staff.save()
        self.staff_token = models.Token.objects.filter(profile=self.staff.profile).first()
        self.staff_token.can_write = True
        self.staff_token.save()

        # Regular user
        self.user = User.objects.create_user(
            username='pos.user',
            first_name='POS',
            last_name='User',
            email='pos@example.com'
        )
        self.user.profile.prepaid_deposit = 50.0
        self.user.profile.save()
        self.user_token = models.Token.objects.filter(profile=self.user.profile).first()

    def test_pos_staff_login(self):
        """Test POS staff login with RFID token."""
        # GET shows login page
        response = self.client.get("/pos/login_staff")
        self.assertEqual(response.status_code, 200)

        # POST with staff RFID token
        response = self.client.post("/pos/login_staff", {
            'rfid_token': f"1\t{self.staff_token.identifier}"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get('profile_id'), self.staff.profile.id)

    def test_pos_user_login(self):
        """Test POS user login (triggers SpaceRentPayment creation)."""
        # Need Price for SpaceRentPayment.daily to exist
        models.Price.objects.create(
            identifier='spaceRentPayment.daily',
            default=10.0,
            members=5.0
        )

        response = self.client.post("/pos/login_user", {
            'rfid_token': f"1\t{self.user_token.identifier}"
        })
        self.assertEqual(response.status_code, 200)

    def test_pos_payment(self):
        """Test POS payment (material payment)."""
        response = self.client.post("/pos/payment", {
            'payment_value': '15.00',
            'rfid_token': f"1\t{self.user_token.identifier}"
        })
        self.assertEqual(response.status_code, 200)

        payment = models.MaterialPayment.objects.filter(creator=self.user).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.price, 15.00)

    def test_pos_write_card(self):
        """Test writing RFID card at POS."""
        # Login staff first
        self.client.post("/pos/login_staff", {
            'rfid_token': f"1\t{self.staff_token.identifier}"
        })

        response = self.client.post("/pos/write_card", {
            'token_value': 'U:newuser;newuuid'
        })
        self.assertEqual(response.status_code, 200)
