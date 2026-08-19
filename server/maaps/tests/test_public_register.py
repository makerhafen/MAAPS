from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import maaps.models as models


class PublicRegisterTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_form_get(self):
        """Test GET request to public registration page."""
        response = self.client.get(reverse('public_register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vorname')
        self.assertContains(response, 'E-Mail')

    def test_register_user_success(self):
        """Test successful public registration creates User, Profile and Token."""
        post_data = {
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice@example.com',
            'company_name': 'Maker Studio',
            'street': 'Hauptstr. 12',
            'postalcode': '20095',
            'city': 'Hamburg'
        }
        response = self.client.post(reverse('public_register'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webif/user/register_success.html')

        # Check created user
        user = User.objects.get(email='alice@example.com')
        self.assertEqual(user.first_name, 'Alice')
        self.assertEqual(user.last_name, 'Smith')
        self.assertEqual(user.username, 'alice.smith')

        # Check profile
        profile = user.profile
        self.assertEqual(profile.company_name, 'Maker Studio')
        self.assertEqual(profile.city, 'Hamburg')
        self.assertFalse(profile.monthly_payment)
        self.assertFalse(profile.commercial_account)

        # Check token
        token = models.Token.objects.filter(profile=profile).first()
        self.assertIsNotNone(token)
        self.assertTrue(token.can_write)

    def test_register_duplicate_email(self):
        """Test registration with existing email triggers validation error."""
        User.objects.create_user(username='existing', email='alice@example.com')
        post_data = {
            'first_name': 'Alice',
            'last_name': 'Duplicate',
            'email': 'alice@example.com',
            'street': 'Test',
            'postalcode': '12345',
            'city': 'Test'
        }
        response = self.client.post(reverse('public_register'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.')
