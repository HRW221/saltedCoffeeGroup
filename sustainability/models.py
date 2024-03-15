import random

from django.utils import timezone

from django.contrib.auth.models import User, AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

from guardiansOfTheGarden import settings


class Userprofile(AbstractUser):
    score = models.IntegerField(default=0)
    bonus_score = models.IntegerField(default=0)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_profiles',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_profiles',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
        related_query_name='user_profile',
    )

    def potd_bonus(self):
        if not self.pk:
            self.bonus_score += 3

    def pack_bonus(self):
        if not self.pk:
            self.bonus_score += 5

    def __str__(self):
        return self.username

    def calculate_score(self):
        users_cards = UsersCard.objects.filter(user_id=self)
        self.score = 0
        for cards in users_cards:
            self.score += cards.card_id.rarity_id.rarity_points
        self.score += self.bonus_score
        self.save()
        return self.score

    def user_owns_all_cards_in_pack(self, userscard):
        card = userscard.card_id
        pack_cards = set(card.get_cards_in_pack())
        user_cards = set(self.get_users_cards())
        return pack_cards.issubset(user_cards)
    def get_users_cards(self):
        return UsersCard.objects.filter(user_id=self).values_list('card_id', flat=True)


class Rarity(models.Model):
    rarity_id = models.AutoField(primary_key=True)
    rarity_desc = models.CharField(max_length=10)
    rarity_points = models.IntegerField()
    rarity_colour = models.CharField(max_length=10)

    def __str__(self):
        return self.rarity_desc


class Pack(models.Model):
    pack_id = models.AutoField(primary_key=True)
    pack_name = models.CharField(max_length=30, default="")

    def __str__(self):
        return self.pack_name


class Card(models.Model):
    card_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="")
    description = models.TextField(default="")
    plant_photo = models.ImageField(default='images/plant_default.jpg', upload_to='static/images')
    rarity_id = models.ForeignKey(Rarity, on_delete=models.CASCADE)
    pack_id = models.ForeignKey(Pack, on_delete=models.CASCADE)

    def get_cards_in_pack(self):
        return Card.objects.filter(pack_id=self.pack_id)

    def __str__(self):
        return self.name


class PlantOfTheDay(models.Model):
    plant = models.ForeignKey(Card, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)  # default=date.today(), blank=True
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        today = timezone.now().date()
        existing_instance = PlantOfTheDay.objects.filter(date=today).first()
        if existing_instance:
            existing_instance.plant = self.plant
            super(PlantOfTheDay, existing_instance).save(*args, **kwargs)
        else:
            super(PlantOfTheDay, self).save(*args, **kwargs)

    def __str__(self):
        return self.plant.name


class UsersCard(models.Model):
    users_cards_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    card_id = models.ForeignKey(Card, on_delete=models.CASCADE)

    def __str__(self):
        return self.card_id.name


import random
import string


def generate_leaderboard_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Leaderboard(models.Model):
    leaderboard_id = models.AutoField(primary_key=True)
    leaderboard_name = models.CharField(max_length=30, default="")
    leaderboard_code = models.CharField(
        max_length=6,
        unique=True,
        editable=False,
        default=generate_leaderboard_code
    )
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.leaderboard_name


class LeaderboardMember(models.Model):
    leaderboard_id = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)
    member_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.member_id.username
