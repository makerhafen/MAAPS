from django.test import TestCase, Client
from django.contrib.auth.models import User
import maaps.models as models


class ApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create user & token
        self.user = User.objects.create_user(
            username='api.user',
            first_name='Api',
            last_name='User',
            email='api@example.com'
        )
        self.user_token = models.Token.objects.filter(profile=self.user.profile).first()

        # Create machine & machine token
        self.machine = models.Machine.objects.create(name='Laser Cutter')
        self.machine.allowed_users.add(self.user)
        self.machine_token = models.Token.objects.create(
            identifier='M:LaserCutter;uuid999',
            machine=self.machine,
            enabled=True
        )

    def test_api_login_and_logout_flow(self):
        """Test API login endpoint creates session and logout ends session."""
        login_url = f"/api/login/M:{self.machine_token.identifier}/{self.user_token.identifier}"
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.decode().startswith("session:"))

        # Check machine current session
        self.machine.refresh_from_db()
        self.assertIsNotNone(self.machine.current_session)
        self.assertEqual(self.machine.current_session.user, self.user)

        # Test API logout
        logout_url = f"/api/logout/M:{self.machine_token.identifier}/{self.user_token.identifier}"
        response = self.client.get(logout_url)
        self.assertEqual(response.status_code, 200)

        self.machine.refresh_from_db()
        self.assertIsNone(self.machine.current_session)

    def test_api_login_unauthorized_user(self):
        """Test API login with unallowed user is rejected."""
        unallowed_user = User.objects.create_user(username='unallowed', email='unallowed@example.com')
        unallowed_token = models.Token.objects.filter(profile=unallowed_user.profile).first()

        login_url = f"/api/login/M:{self.machine_token.identifier}/{unallowed_token.identifier}"
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 400)

        # Machine session should not be created
        self.machine.refresh_from_db()
        self.assertIsNone(self.machine.current_session)
