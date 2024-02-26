from django.contrib import admin
from .models import PlantOfTheDay, Plant, Rarity, Card
from .models import PlantOfTheDay, Plant, Card, Rarity

admin.site.register(PlantOfTheDay)
admin.site.register(Plant)
admin.site.register(Rarity)
admin.site.register(Card)

# Register your models here.
