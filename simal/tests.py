from django.test import TestCase
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm


class TestCustomUserCreationForm(TestCase):
    def setUp(self):
        # Create a test user for duplicate validation checks
        self.existing_user = User.objects.create(
            username="existinguser", email="existing@test.com"
        )

    def test_valid_form(self):
        # Test with valid data
        form_data = {"username": "newuser", "email": "newuser@test.com"}
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_duplicate_username(self):
        # Test with existing username
        form_data = {"username": "existinguser", "email": "different@test.com"}
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Este nome de usuário já está em uso.", form.errors["username"])

    def test_duplicate_email(self):
        # Test with existing email
        form_data = {"username": "differentuser", "email": "existing@test.com"}
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Este e-mail já está em uso.", form.errors["email"])

    def test_blank_fields(self):
        # Test with empty fields
        form_data = {"username": "", "email": ""}
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["username"])  # Username is required
        self.assertTrue(form.errors["email"])  # Email is required

    def tearDown(self):
        # Clean up created test data
        User.objects.all().delete()
