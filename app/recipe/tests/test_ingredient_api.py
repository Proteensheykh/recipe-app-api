from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class TestPublicIngredientApi(TestCase):
    """Test request from unauthenticated/anonymouse user"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login required to access api endpoints"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateIngredientApi(TestCase):
    """Test request from authenticated user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user1@email.com',
            password='user1pass'
        )

        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""

        Ingredient.objects.create(user=self.user, name='beans')
        Ingredient.objects.create(user=self.user, name='onions')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test that only ingredients for authenticated user is returned"""
        user2 = get_user_model().objects.create_user(
            email='user2@mail.com',
            password='user2pass'
        )

        userIngredient = Ingredient.objects.create(
            user=self.user,
            name='cucumber'
            )
        Ingredient.objects.create(user=user2, name='mayonnaise')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], userIngredient.name)

    def test_create_ingredient_successful(self):
        """Test create ingredient"""
        payload = {'name': 'pasta'}

        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.all().filter(
            name=payload['name'],
            user=self.user
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test ingredient is not created with invalid payload"""
        payload = {'name': ''}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
