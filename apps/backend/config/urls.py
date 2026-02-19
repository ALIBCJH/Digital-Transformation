from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from core.views import (
    RegisterView, LoginView, CreateRegionalAdminView, MemberCreateView, AltarListView,
    LogoutView, MemberListView, RegionalDashboardView, AltarDashboardView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication endpoints
    path('api/register/', RegisterView.as_view(), name='register'),  # Altar-level admin signup
    path('api/admin/create-regional/', CreateRegionalAdminView.as_view(), name='create_regional_admin'),  # Regional/sub-regional admin (superuser only)
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Member endpoints
    path('api/members/create/', MemberCreateView.as_view(), name='member_create'),
    path('api/members/list/', MemberListView.as_view(), name='member_list'),
    # Dashboard/Reports endpoints
    path('api/dashboard/regional/', RegionalDashboardView.as_view(), name='regional_dashboard'),
    path('api/dashboard/altar/', AltarDashboardView.as_view(), name='altar_dashboard'),
    # TODO: Re-enable after creating MemberTransferHistory model
    # path('api/members/transfer/', MemberTransferView.as_view(), name='member_transfer'),
    # TODO: Re-enable after creating Guest model
    # path('api/guests/create/', GuestCreateView.as_view(), name='guest_create'),
    # TODO: Re-enable after creating AttendanceLog model
    # path('api/attendance/record/', BulkAttendanceView.as_view(), name='attendance_record'),
    # List all available altars
    path('api/altars/', AltarListView.as_view(), name='altar_list'),
]
