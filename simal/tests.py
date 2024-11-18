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
        form_data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        if not form.is_valid():
            print(form.errors)  # Adiciona esta linha para depuração
        self.assertTrue(form.is_valid())

    def test_duplicate_username(self):
        # Test with existing username
        form_data = {
            "username": "existinguser",
            "email": "different@test.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Um usuário com este nome de usuário já existe.", form.errors["username"]
        )

    def test_duplicate_email(self):
        # Test with existing email
        form_data = {
            "username": "differentuser",
            "email": "existing@test.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Um usuário com este endereço de e-mail já existe.", form.errors["email"]
        )

    def test_blank_fields(self):
        # Test with empty fields
        form_data = {"username": "", "email": "", "password1": "", "password2": ""}
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["username"])  # Username is required
        self.assertTrue(form.errors["email"])  # Email is required

    def tearDown(self):
        # Clean up created test data
        User.objects.all().delete()
