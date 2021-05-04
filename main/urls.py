from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user', views.user, name='user'),
    path('authlogin', views.AuthLoginTalent.as_view(), name='authlogin'),
    path('authcomplete', views.AuthCompleteTalent.as_view(), name='authcomplete'),
    path('logout', views.LogoutTalent.as_view(), name='logout'),
    path('auth_steam', views.auth_steam, name='auth_steam'),
    path('logout_steam', views.logout_steam, name='logout_steam'),
    path('auth_blizzard', views.auth_blizzard, name='auth_blizzard'),
    path('logout_blizzard', views.logout_blizzard, name='logout_blizzard'),
]


