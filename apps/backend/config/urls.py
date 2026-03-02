from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from core.views import (
    AltarDashboardView,
    AltarListView,
    CreateRegionalAdminView,
    LoginView,
    LogoutView,
    MemberCreateView,
    MemberListView,
    MemberTransferView,
    RegionalDashboardView,
    RegisterView,
    SuperAdminDashboardView,
    SuperAdminRegisterView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication endpoints
    path(
        "api/register/", RegisterView.as_view(), name="register"
    ),  # Altar-level admin signup
    path(
        "api/superadmin/create/",
        SuperAdminRegisterView.as_view(),
        name="superadmin_create",
    ),  # Regional/sub-regional superadmin
    # Regional/sub-regional admin (superuser only)
    path(
        "api/admin/create-regional/",
        CreateRegionalAdminView.as_view(),
        name="create_regional_admin",
    ),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Member endpoints
    path("api/members/create/", MemberCreateView.as_view(), name="member_create"),
    path("api/members/list/", MemberListView.as_view(), name="member_list"),
    path("api/members/transfer/", MemberTransferView.as_view(), name="member_transfer"),
    # Dashboard/Reports endpoints
    path(
        "api/dashboard/superadmin/",
        SuperAdminDashboardView.as_view(),
        name="superadmin_dashboard",
    ),
    path(
        "api/dashboard/regional/",
        RegionalDashboardView.as_view(),
        name="regional_dashboard",
    ),
    path("api/dashboard/altar/", AltarDashboardView.as_view(), name="altar_dashboard"),
    # Attendance endpoints
    # TODO: Re-enable after creating GetMembersForAttendanceView
    # path(
    #     "api/attendance/members/",
    #     GetMembersForAttendanceView.as_view(),
    #     name="get_members_for_attendance",
    # ),
    # TODO: Re-enable after creating BulkAttendanceView
    # path(
    #     "api/attendance/record/", BulkAttendanceView.as_view(), name="bulk_attendance"
    # ),
    # TODO: Re-enable after creating Guest model
    # path('api/guests/create/', GuestCreateView.as_view(), name='guest_create'),
    # List all available altars
    path("api/altars/", AltarListView.as_view(), name="altar_list"),
]
