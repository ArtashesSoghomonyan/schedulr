from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    BrowserCompatibleTokenObtainPairView,
    LogoutView,
    MeView,
    SignupView,
)

urlpatterns = [
    path("login/", BrowserCompatibleTokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signup/", SignupView.as_view(), name="signup"),
]
