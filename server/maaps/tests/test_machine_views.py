from django.test import TestCase, Client
from django.contrib.auth.models import User
import maaps.models as models


class MachineViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # User and Profile
        self.user = User.objects.create_user(
            username='machine.operator',
            first_name='Operator',
            last_name='User',
            email='operator@example.com'
        )
        self.user_token = models.Token.objects.filter(profile=self.user.profile).first()

        # Machine and Machine Token
        self.machine = models.Machine.objects.create(
            name='CNC Router',
            ask_clean=True,
            ask_pay_material=True
        )
        self.machine.allowed_users.add(self.user)

        self.machine_token = models.Token.objects.create(
            identifier='M:CNCRouter;uuid555',
            machine=self.machine,
            enabled=True
        )

    def test_machine_login_and_user_session_flow(self):
        """Test logging machine in, user logging in, showing session and logout."""
        # Step 1: Login machine via URL token (without "M:" prefix!)
        machine_token_part = "CNCRouter;uuid555"
        response = self.client.get(f"/machine/M:{machine_token_part}")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get('machine_id'), self.machine.id)

        # Step 2: Login user to machine
        response = self.client.post("/machine/login_user", {
            'rfid_token': f"1\t{self.user_token.identifier}"
        })
        self.assertEqual(response.status_code, 302)

        self.machine.refresh_from_db()
        self.assertIsNotNone(self.machine.current_session)
        self.assertEqual(self.machine.current_session.user, self.user)

        # Step 3: View session
        response = self.client.get("/machine/show_session")
        self.assertEqual(response.status_code, 200)

        # Step 4: Logout user - renders template (200)
        response = self.client.get("/machine/logout_user")
        self.assertEqual(response.status_code, 200)

        self.machine.refresh_from_db()
        self.assertIsNone(self.machine.current_session)

    def test_machine_rate_cleanliness(self):
        """Test rating cleanliness on logout."""
        session = models.MachineSession.objects.create(
            machine=self.machine,
            user=self.user
        )
        self.machine.current_session = session
        self.machine.save()

        # Set session in client
        s = self.client.session
        s['machine_id'] = self.machine.id
        s.save()

        response = self.client.post("/machine/rate_machine", {'clean_rating': '5'})
        self.assertEqual(response.status_code, 302)

        session.refresh_from_db()
        self.assertEqual(session.rating_clean, 5)

    def test_machine_pay_material(self):
        """Test paying material at machine session."""
        session = models.MachineSession.objects.create(
            machine=self.machine,
            user=self.user
        )
        self.machine.current_session = session
        self.machine.save()

        s = self.client.session
        s['machine_id'] = self.machine.id
        s.save()

        # Need to include rfid_token for get_profile_from_post
        response = self.client.post("/machine/pay_material", {
            'payment_value': '12.50',
            'rfid_token': f"1\t{self.user_token.identifier}"
        })
        self.assertEqual(response.status_code, 200)

        material_payment = models.MaterialPayment.objects.filter(machinesession=session).first()
        self.assertIsNotNone(material_payment)
        self.assertEqual(material_payment.price, 12.50)
