from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@mail.com', password='testPassword'):
    """Creates sample test user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with email is successfull"""

        email = "mo@gobe.com"
        password = "Bigmanting"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEquals(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test that new user email is normalised"""

        email = 'mo@GOBE.com'
        user = get_user_model().objects.create_user(email, 'abc123')

        self.assertEquals(user.email, email.lower())

    def test_new_user_valid_email(self):
        """Test creating a new user with no email raises error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_new_super_user(self):
        """Test creating a new superuser"""

        user = get_user_model().objects.create_superuser(
            'mo@gobe.com',
            'test123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_str(self):
        """Test tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='vegan'
        )

        self.assertEquals(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test Ingredient string reprsentation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Oregano"
        )

        self.assertEqual(str(ingredient), ingredient.name)
