from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import RegisterView


urlpatterns = [
    path('admin/', admin.site.urls),
    # Sign up endpoint
    path('api/register/', RegisterView.as_view(), name='auto_register'),
    # Login endpoint
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Refresh Token to get the new token when the old one expires
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
