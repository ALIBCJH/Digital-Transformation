from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# Ensure these imports are correctly configured in your project
from core.models import (
    Altar,
    Guest,
    Member,
    MemberTransferHistory,
    OrganizationNode,
    User,
)

from .permissions import CanManageMembers, CanTransferMembers, HasOrganizationalScope
from .serializers import (
    LoginSerializer,
    MemberSerializer,
    MemberTransferSerializer,
    RegisterSerializer,
    SuperAdminRegisterSerializer,
)


def health_check(request):
    """Simple health check endpoint for monitoring."""
    return HttpResponse("OK", status=200)


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint - Sign up with first name, last name,
    email/phone, altar, and password
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for auto-login after registration
        refresh = RefreshToken.for_user(user)

        # Determine role and scope
        role = "admin"
        if user.admin_scope:
            scope = user.admin_scope.code
            scope_name = user.admin_scope.name
        else:
            scope = "altar"
            scope_name = user.home_altar.name if user.home_altar else "No Scope"

        return Response(
            {
                "message": "Admin account created successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": role,
                    "scope": scope,
                    "scope_name": scope_name,
                    "home_altar": user.home_altar.name if user.home_altar else None,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class SuperAdminRegisterView(generics.CreateAPIView):
    """
    Create regional/sub-regional superadmin.
    Public endpoint for initial setup - creates admins with organizational scope.
    """

    queryset = User.objects.all()
    serializer_class = SuperAdminRegisterSerializer
    # TODO: In production, enforce authentication/master key to restrict access
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": f"Superadmin account created for {user.admin_scope.name}",
                "admin": {
                    "username": user.username,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "email": user.email,
                    "phoneNumber": user.phone_number,
                    "scope": user.admin_scope.code,
                    "scopeName": user.admin_scope.name,
                    "scopeDepth": user.admin_scope.depth,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class CreateRegionalAdminView(APIView):
    """
    Create a regional or sub-regional admin with higher scope.
    Only superusers can access this endpoint.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only superusers can create regional admins
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmins can create regional administrators"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate required fields
        required_fields = [
            "first_name",
            "last_name",
            "email_or_phone",
            "scope_code",
            "password",
        ]
        for field in required_fields:
            if not request.data.get(field):
                return Response(
                    {"error": f"Field '{field}' is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        email_or_phone = request.data["email_or_phone"]
        scope_code = request.data["scope_code"]
        password = request.data["password"]

        # Lookup the organizational node
        try:
            scope_node = OrganizationNode.objects.get(code=scope_code, is_active=True)
        except OrganizationNode.DoesNotExist:
            return Response(
                {"error": f"Node with code '{scope_code}' does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate unique username
        username = f"{first_name.lower()}.{last_name.lower()}"
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Determine if email or phone is provided
        user_data = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "admin_scope": scope_node,
            "is_staff": True,
            "is_superuser": False,
        }

        if "@" in email_or_phone:
            if User.objects.filter(email=email_or_phone).exists():
                return Response(
                    {"error": "A user with this email already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_data["email"] = email_or_phone
            user_data["phone_number"] = None
        else:
            if User.objects.filter(phone_number=email_or_phone).exists():
                return Response(
                    {"error": "A user with this phone already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_data["phone_number"] = email_or_phone
            user_data["email"] = ""

        # Create the regional admin
        user = User.objects.create_user(**user_data)

        return Response(
            {
                "message": f"Regional admin created for {scope_node.name}",
                "admin": {
                    "username": user.username,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "scope": scope_node.code,
                    "scopeName": scope_node.name,
                    "scopeDepth": scope_node.depth,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """User login endpoint - Login with email/phone and password"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Determine role and scope for response
        if user.is_superuser:
            role = "superadmin"
            scope = "global"
            scope_name = "All Regions"
        elif user.admin_scope:
            role = "admin"
            scope = user.admin_scope.code
            scope_name = user.admin_scope.name
        else:
            role = "admin"
            scope = "unassigned"
            scope_name = "No Scope Assigned"

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "role": role,
                    "scope": scope,
                    "scopeName": scope_name,
                    "homeAltar": user.home_altar.name if user.home_altar else None,
                },
            },
            status=status.HTTP_200_OK,
        )


class MemberCreateView(generics.CreateAPIView):
    """Create new church members (filtered by organizational scope)"""

    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated, HasOrganizationalScope, CanManageMembers]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate that the altar is within admin's scope
        altar = serializer.validated_data.get("home_altar")
        if not request.user.is_superuser and not request.user.can_manage_altar(altar):
            return Response(
                {
                    "error": (
                        f"You don't have permission to create members for "
                        f"'{altar.name}'. You can only manage altars within your "
                        f"organizational scope."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        member = serializer.save()

        return Response(
            {
                "message": "Member created successfully",
                "member": MemberSerializer(member).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AltarListView(generics.ListAPIView):
    """List all available altars within admin's organizational scope"""

    permission_classes = [AllowAny]  # Allow unauthenticated access for signup

    def get(self, request, *args, **kwargs):
        # Base queryset based on user's scope
        if request.user.is_authenticated:
            if request.user.is_superuser:
                altars = Altar.objects.filter(is_active=True).select_related(
                    "parent_node", "pastor"
                )
            else:
                altars = request.user.get_accessible_altars().select_related(
                    "parent_node", "pastor"
                )
        else:
            altars = Altar.objects.filter(is_active=True).select_related(
                "parent_node", "pastor"
            )

        # Optional filters
        region = request.query_params.get("region")
        sub_region = request.query_params.get("sub_region")
        city = request.query_params.get("city")

        if region:
            altars = altars.filter(parent_node__code=region)
        if sub_region:
            altars = altars.filter(parent_node__code=sub_region)
        if city:
            altars = altars.filter(city__icontains=city)

        # Prepare detailed response
        altar_list = []
        for altar in altars:
            member_count = Member.objects.filter(
                home_altar=altar, is_active=True
            ).count()
            altar_list.append(
                {
                    "id": altar.id,
                    "name": altar.name,
                    "code": altar.code,
                    "city": altar.city,
                    "address": altar.address,
                    "parent_region": altar.parent_node.name
                    if altar.parent_node
                    else None,
                    "parent_code": altar.parent_node.code
                    if altar.parent_node
                    else None,
                    "pastor": altar.pastor.get_full_name()
                    if altar.pastor
                    else "Not Assigned",
                    "member_count": member_count,
                    "capacity": altar.capacity,
                    "established_date": altar.established_date,
                }
            )

        scope_name = "Global"
        if request.user.is_authenticated and request.user.admin_scope:
            scope_name = request.user.admin_scope.name

        return Response(
            {
                "count": len(altar_list),
                "scope": scope_name,
                "altars": altar_list,
            },
            status=status.HTTP_200_OK,
        )


class MemberTransferView(APIView):
    """
    Transfer member to another altar or offboard them (deactivate).
    Filtered by organizational scope.
    """

    permission_classes = [IsAuthenticated, HasOrganizationalScope, CanTransferMembers]

    @transaction.atomic
    def post(self, request):
        serializer = MemberTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = serializer.validated_data["member_id"]
        to_altar = serializer.validated_data.get("to_altar_id")
        reason = serializer.validated_data["reason"]
        notes = serializer.validated_data.get("notes", "")

        # Verify admin has permission for source altar
        if not request.user.is_superuser and not request.user.can_manage_altar(
            member.home_altar
        ):
            return Response(
                {
                    "error": (
                        f"You don't have permission to transfer members from "
                        f"'{member.home_altar.name}'."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # If transferring, verify admin has permission for destination altar
        if to_altar:
            if not request.user.is_superuser and not request.user.can_manage_altar(
                to_altar
            ):
                return Response(
                    {
                        "error": (
                            f"You don't have permission to transfer members to "
                            f"'{to_altar.name}'."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        # Record the transfer
        from_altar = member.home_altar

        transfer_record = MemberTransferHistory.objects.create(
            member=member,
            from_altar=from_altar,
            to_altar=to_altar,
            transfer_reason=reason,
            notes=notes,
            processed_by=request.user,
        )

        # Update member status
        if to_altar:
            member.home_altar = to_altar
            member.save()
            action = "transferred"
            message = (
                f"Member '{member.full_name}' successfully transferred "
                f"from '{from_altar.name}' to '{to_altar.name}'"
            )
        else:
            member.is_active = False
            member.save()
            action = "offboarded"
            message = (
                f"Member '{member.full_name}' successfully offboarded "
                f"from '{from_altar.name}'"
            )

        return Response(
            {
                "message": message,
                "transfer": {
                    "id": transfer_record.id,
                    "member": member.full_name,
                    "from_altar": from_altar.name,
                    "to_altar": to_altar.name if to_altar else None,
                    "reason": reason,
                    "action": action,
                    "transferred_at": transfer_record.created_at,
                    "transferred_by": request.user.get_full_name(),
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Logout endpoint - blacklist the refresh token"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Successfully logged out"}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Invalid token or token already blacklisted"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MemberListView(generics.ListAPIView):
    """List members for attendance marking (filtered by scope)"""

    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated, HasOrganizationalScope]

    def get_queryset(self):
        """Get active members within admin's organizational scope"""
        queryset = Member.objects.filter(is_active=True).select_related("home_altar")

        # Superusers see all members
        if not self.request.user.is_superuser:
            # Regular admins only see members within their scope
            accessible_altars = self.request.user.get_accessible_altars()
            queryset = queryset.filter(home_altar__in=accessible_altars)

        # Optional filter by altar
        altar_name = self.request.query_params.get("altar", None)
        if altar_name:
            queryset = queryset.filter(home_altar__name=altar_name)

        return queryset.order_by("full_name")


class RegionalDashboardView(APIView):
    """
    Regional dashboard showing aggregated metrics.
    """

    permission_classes = [IsAuthenticated, HasOrganizationalScope]

    def get(self, request):
        user = request.user

        # Get the organizational scope
        if user.is_superuser:
            root_nodes = OrganizationNode.objects.filter(
                parent__isnull=False, depth=1, is_active=True
            )
            scope_name = "All Regions"
        elif user.admin_scope:
            root_nodes = [user.admin_scope]
            scope_name = user.admin_scope.name
        else:
            return Response(
                {"error": "No organizational scope assigned"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Build regional report
        regional_data = []

        for region in root_nodes:
            # Get all descendant nodes
            sub_regions = region.get_descendants(include_self=False).filter(
                is_active=True
            )

            altars_in_region = Altar.objects.filter(
                parent_node__in=region.get_descendants(include_self=True),
                is_active=True,
            )

            members_in_region = Member.objects.filter(
                home_altar__in=altars_in_region, is_active=True
            )

            total_altars = altars_in_region.count()
            total_members = members_in_region.count()
            total_sub_regions = sub_regions.count()

            # Gender breakdown
            male_count = members_in_region.filter(gender="M").count()
            female_count = members_in_region.filter(gender="F").count()

            # Sub-region breakdown
            sub_region_breakdown = []
            for sub_region in sub_regions:
                altars_in_sub = Altar.objects.filter(
                    parent_node=sub_region, is_active=True
                )
                members_in_sub = Member.objects.filter(
                    home_altar__in=altars_in_sub, is_active=True
                )

                sub_region_breakdown.append(
                    {
                        "name": sub_region.name,
                        "code": sub_region.code,
                        "total_altars": altars_in_sub.count(),
                        "total_members": members_in_sub.count(),
                        "altars": [
                            {
                                "name": altar.name,
                                "city": altar.city,
                                "member_count": Member.objects.filter(
                                    home_altar=altar, is_active=True
                                ).count(),
                            }
                            for altar in altars_in_sub
                        ],
                    }
                )

            regional_data.append(
                {
                    "region": {
                        "name": region.name,
                        "code": region.code,
                        "leader": region.current_leader.get_full_name()
                        if region.current_leader
                        else "Not Assigned",
                    },
                    "summary": {
                        "total_sub_regions": total_sub_regions,
                        "total_altars": total_altars,
                        "total_members": total_members,
                        "male_members": male_count,
                        "female_members": female_count,
                        "total_guests": 0,
                        "total_present_today": 0,
                        "total_absent_today": 0,
                    },
                    "sub_regions": sub_region_breakdown,
                }
            )

        return Response(
            {
                "scope": scope_name,
                "report_date": timezone.now().date(),
                "regions": regional_data,
            },
            status=status.HTTP_200_OK,
        )


class AltarDashboardView(APIView):
    """
    Individual altar dashboard showing detailed metrics.
    """

    permission_classes = [IsAuthenticated, HasOrganizationalScope]

    def get(self, request):
        user = request.user

        # Get altar from query params or user's scope
        altar_name = request.query_params.get("altar")

        if altar_name:
            try:
                altar = Altar.objects.get(name=altar_name, is_active=True)
            except Altar.DoesNotExist:
                return Response(
                    {"error": f"Altar '{altar_name}' not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not user.is_superuser and not user.can_manage_altar(altar):
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            accessible_altars = user.get_accessible_altars()
            if accessible_altars.count() == 0:
                return Response(
                    {"error": "No altars accessible"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            altar = accessible_altars.first()

        members = Member.objects.filter(home_altar=altar, is_active=True)

        total_members = members.count()
        male_count = members.filter(gender="M").count()
        female_count = members.filter(gender="F").count()

        departments = (
            members.values("serving_department")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return Response(
            {
                "altar": {
                    "name": altar.name,
                    "code": altar.code,
                    "city": altar.city,
                    "pastor": altar.pastor.get_full_name()
                    if altar.pastor
                    else "Not Assigned",
                    "parent_region": altar.parent_node.name
                    if altar.parent_node
                    else None,
                },
                "summary": {
                    "total_members": total_members,
                    "male_members": male_count,
                    "female_members": female_count,
                    "total_guests": 0,
                    "present_today": 0,
                    "absent_today": 0,
                    "attendance_rate": 0.0,
                },
                "departments": list(departments),
                "recent_members": [
                    {
                        "id": m.id,
                        "full_name": m.full_name,
                        "phone_number": m.phone_number,
                        "gender": m.gender,
                        "serving_department": m.serving_department,
                        "membership_date": m.membership_date,
                    }
                    for m in members.order_by("-created_at")[:10]
                ],
            },
            status=status.HTTP_200_OK,
        )


class SuperAdminDashboardView(APIView):
    """
    Comprehensive dashboard for regional/sub-regional superadmins.
    """

    permission_classes = [IsAuthenticated, HasOrganizationalScope]

    def get(self, request):
        user = request.user

        if user.is_superuser:
            scope_node = None
            scope_name = "Global - All Regions"
            all_nodes = OrganizationNode.objects.filter(is_active=True)
            all_altars = Altar.objects.filter(is_active=True)
        elif user.admin_scope:
            scope_node = user.admin_scope
            scope_name = scope_node.name
            all_nodes = scope_node.get_descendants(include_self=True)
            all_altars = Altar.objects.filter(parent_node__in=all_nodes, is_active=True)
        else:
            return Response(
                {"error": "No scope assigned"}, status=status.HTTP_403_FORBIDDEN
            )

        all_members = Member.objects.filter(home_altar__in=all_altars, is_active=True)
        all_guests = Guest.objects.filter(visited_altar__in=all_altars)

        total_regions = all_nodes.filter(depth=1).count() if not scope_node else 0
        total_sub_regions = (
            all_nodes.filter(depth=2).count()
            if not scope_node
            else all_nodes.exclude(id=scope_node.id).count()
        )
        total_altars = all_altars.count()
        total_members = all_members.count()
        total_male = all_members.filter(gender="M").count()
        total_female = all_members.filter(gender="F").count()
        total_guests = all_guests.count()

        today = timezone.now().date()
        current_month_start = today.replace(day=1)

        new_members_this_month = all_members.filter(
            created_at__gte=current_month_start
        ).count()
        members_last_month = all_members.filter(
            created_at__lt=current_month_start
        ).count()

        growth_rate = (
            ((new_members_this_month) / members_last_month) * 100
            if members_last_month > 0
            else (100.0 if new_members_this_month > 0 else 0.0)
        )

        regional_breakdown = []
        if user.is_superuser:
            regions = OrganizationNode.objects.filter(depth=1, is_active=True)
        elif scope_node and scope_node.depth <= 1:
            regions = scope_node.get_children()
        else:
            regions = []

        for region in regions:
            region_altars = Altar.objects.filter(
                parent_node__in=region.get_descendants(include_self=True),
                is_active=True,
            )
            region_members = Member.objects.filter(
                home_altar__in=region_altars, is_active=True
            )
            region_guests = Guest.objects.filter(visited_altar__in=region_altars)

            regional_breakdown.append(
                {
                    "name": region.name,
                    "code": region.code,
                    "total_altars": region_altars.count(),
                    "total_members": region_members.count(),
                    "total_guests": region_guests.count(),
                    "leader": region.current_leader.get_full_name()
                    if region.current_leader
                    else "Not Assigned",
                }
            )

        top_altars = []
        for altar in all_altars.order_by("-member_count")[:10]:
            altar_members = Member.objects.filter(
                home_altar=altar, is_active=True
            ).count()
            altar_guests = Guest.objects.filter(visited_altar=altar).count()

            top_altars.append(
                {
                    "name": altar.name,
                    "city": altar.city,
                    "member_count": altar_members,
                    "guest_count": altar_guests,
                    "pastor": altar.pastor.get_full_name()
                    if altar.pastor
                    else "Not Assigned",
                }
            )

        return Response(
            {
                "scope": scope_name,
                "report_date": timezone.now().date(),
                "summary": {
                    "total_regions": total_regions,
                    "total_sub_regions": total_sub_regions,
                    "total_altars": total_altars,
                    "total_members": total_members,
                    "total_male": total_male,
                    "total_female": total_female,
                    "total_guests": total_guests,
                    "growth_rate": growth_rate,
                },
                "regional_breakdown": regional_breakdown,
                "top_altars": top_altars,
            },
            status=status.HTTP_200_OK,
        )
