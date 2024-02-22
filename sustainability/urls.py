from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("user/", views.account_view, name="user"),
    path("leaderboard/", views.leaderboard_view, name="leaderboard"),
    path("admin/plant-of-the-day/", views.plant_of_the_day_view, name="plant_of_the_day_view")
]