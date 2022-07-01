from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag
# from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class TestPublicTagsAPI(TestCase):
    """Test Tag api requests by authenticated/anonymous User"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that authentication is required to call tags url"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateTagsAPI(TestCase):
    """Test tag API requests by authenticated User"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user1@mail.com',
            password='User1password'
        )
        self.user2 = get_user_model().objects.create_user(
            email='user2@mail.com',
            password='User2password'
        )

        # self.user has 3 tags assigned (vegan, dessert, comfort food)
        # while self.user2 has just 1 tag assigned (Dairy)
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        Tag.objects.create(user=self.user, name='comfort food')
        Tag.objects.create(user=self.user2, name='Dairy')

        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_tags(self):
        """Test retrieve authenticated user's tags list"""
        res = self.client.get(TAGS_URL)

        # tags = Tag.objects.all().order_by('-name')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)
        # assert that user2's tag is not contained in user's response
        self.assertNotIn(self.user2.tag_set.all(), self.user.tag_set.all())

    def test_tag_create_successful(self):
        """Test creating new Tag"""
        payload = {'name': 'Test tag'}
        res = self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_tag(self):
        """Test invalid tags are not created"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
