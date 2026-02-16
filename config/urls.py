from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import (
    RegisterView, MemberCreateView, AltarListView,
    GuestCreateView, MemberTransferView, LogoutView,
    MemberListView, BulkAttendanceView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication endpoints
    path('api/register/', RegisterView.as_view(), name='auto_register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Member endpoints
    path('api/members/create/', MemberCreateView.as_view(), name='member_create'),
    path('api/members/list/', MemberListView.as_view(), name='member_list'),
    path('api/members/transfer/', MemberTransferView.as_view(), name='member_transfer'),
    # Guest onboarding endpoint
    path('api/guests/create/', GuestCreateView.as_view(), name='guest_create'),
    # Attendance endpoints
    path('api/attendance/record/', BulkAttendanceView.as_view(), name='attendance_record'),
    # List all available altars
    path('api/altars/', AltarListView.as_view(), name='altar_list'),
]
