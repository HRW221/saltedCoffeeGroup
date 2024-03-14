from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("user/", views.account_view, name="user"),
    path("user/cards", views.users_cards_view, name="cards"),
    path("user/account", views.user_account_view, name="account"),
    path("user/identify-plant/upload-plant-image/", views.upload_plant_view, name="upload_plant_image"),
    path("user/identify-plant/capture-plant-image/", views.capture_plant_view, name="capture_plant_image"),
    path("user/identify-plant/", views.identify_plant_view, name="identify_plant_view"),
    path("leaderboard/", views.leaderboard_view, name="leaderboard"),
    path("admin/plant-of-the-day/", views.plant_of_the_day_view, name="plant_of_the_day_view")
]