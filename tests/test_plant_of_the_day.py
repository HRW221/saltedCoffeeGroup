from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse

from sustainability.models import PlantOfTheDay, Plant, Rarity, Card
from sustainability.permissions import ADD_PLANT_OF_THE_DAY


class TestPlantOfTheDay(TestCase):
    def setUp(self):
        content_type = ContentType.objects.get_for_model(PlantOfTheDay)
        self.plant_of_the_day_permission, _ = Permission.objects.get_or_create(
            codename=ADD_PLANT_OF_THE_DAY,
            name='Can add plant of the day',
            content_type=content_type
        )
        self.user_admin = User.objects.create_user(
            username='test_user_admin',
            email='test_email_admin',
            password='test_password_admin')
        self.user_non_admin = User.objects.create_user(
            username='test_user_non_admin',
            email='test_email_non_admin',
            password='test_password_non_admin')
        self.rarity = Rarity.objects.create(
            rarity_id='1',
            rarity_desc='common',
            rarity_colour='red',
            rarity_points=5
            )
        self.plant = Plant.objects.create(
            name='test_plant',
            plant_id=1,
            description='test_plant_description')
        self.card = Card.objects.create(
            plant_id=self.plant,
            rarity_id=self.rarity
        )
        self.user_admin.user_permissions.add(self.plant_of_the_day_permission)
        self.user_admin = get_object_or_404(User, pk=self.user_admin.pk)

    def test_add_game_master(self):
        self.client.login(username='test_user_admin', password='test_password_admin')
        response = self.client.post(reverse('plant_of_the_day_view'), {'plant': self.card.pk})
        self.assertIn(self.plant_of_the_day_permission, self.user_admin.user_permissions.all(),
                      msg='Did not assign permission to game master.')
        self.assertEqual(response.status_code, 302, msg='Did not redirect properly')
        self.assertEqual(PlantOfTheDay.objects.count(), 1, msg='User did not add plant but is a game master')

    def test_add_non_game_master(self):
        self.client.login(username='test_user_non_admin', password='test_password_non_admin')
        response = self.client.post(reverse('plant_of_the_day_view'), {'plant': self.card.pk})
        self.assertFalse(self.user_non_admin.has_perm(ADD_PLANT_OF_THE_DAY),
                         msg='The user is not a game master and should not have permission to add plant of the day')
        self.assertEqual(response.status_code, 403, msg='Non-admin did not receive forbidden response')
        self.assertEqual(PlantOfTheDay.objects.count(), 0, msg='User added plant but is not a game master')
