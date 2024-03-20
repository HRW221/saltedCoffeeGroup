from django.contrib import admin
from .models import Userprofile, Rarity, Pack, Card, PlantOfTheDay, UsersCard, Leaderboard, LeaderboardMember, \
    GameMasterCode

admin.site.register(Userprofile)
admin.site.register(Rarity)
admin.site.register(Pack)
admin.site.register(Card)


class potdAdmin(admin.ModelAdmin):
    readonly_fields = ("date",)


class leaderboardAdmin(admin.ModelAdmin):
    readonly_fields = ("leaderboard_code",)


admin.site.register(PlantOfTheDay, potdAdmin)
admin.site.register(UsersCard)
admin.site.register(Leaderboard, leaderboardAdmin)
admin.site.register(LeaderboardMember)
admin.site.register(GameMasterCode)
