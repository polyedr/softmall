from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import MeView, RegisterCompanyView, RegisterUserView


urlpatterns = [
    path("auth/register-company", RegisterCompanyView.as_view(), name="register-company"),
    path("auth/register", RegisterUserView.as_view(), name="register-user"),
    path("auth/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("me", MeView.as_view(), name="me"),
]
