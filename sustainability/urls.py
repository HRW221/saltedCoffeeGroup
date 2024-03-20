from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("user/", views.account_view, name="user"),
    path("user/cards", views.users_cards_view, name="cards"),
    path("user/account", views.user_account_view, name="account"),
    path("user/change_details/", views.change_details, name="change_details"),
    path("user/delete_account", views.delete_account, name="delete_account"),
    path("user/identify-plant/upload-plant-image/", views.upload_plant_view, name="upload_plant_image"),
    path("user/identify-plant/capture-plant-image/", views.capture_plant_view, name="capture_plant_image"),
    path("exeter-info", views.exeter_view, name="exeter"),
    path("user/identify-plant/", views.identify_plant_view, name="identify_plant_view"),
    path("leaderboards/", views.leaderboard_list_view, name="leaderboard"),
    path('leaderboards/<int:leaderboard_id>/', views.leaderboard_view, name='leaderboard_detail'),
    path('leaderboards/create/', views.create_leaderboard_view, name='create_leaderboard'),
    path('leaderboards/join/', views.join_leaderboard, name='join_leaderboard'),
    path('leaderboards/leave/<int:leaderboard_id>/', views.leave_leaderboard, name='leave_leaderboard'),
    path("admin/plant-of-the-day/", views.plant_of_the_day_view, name="plant_of_the_day_view"),
    path("admin/gamemastercreation/", views.code_enter_view, name="code_enter_view")
]