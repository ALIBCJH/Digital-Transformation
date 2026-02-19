from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction, models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from core.models import User, Member, Altar, OrganizationNode
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, MemberSerializer
)
from .permissions import (
    HasOrganizationalScope, CanManageMembers
)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint - Sign up with first name, last name, email/phone, altar, and password"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "Admin account created successfully. Please login to continue."
        }, status=status.HTTP_201_CREATED)


class CreateRegionalAdminView(APIView):
    """
    Create a regional or sub-regional admin with higher scope.
    This endpoint creates admins who can manage entire regions/sub-regions.
    Only superusers can access this endpoint.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Only superusers can create regional admins
        if not request.user.is_superuser:
            return Response({
                "error": "Only superadmins can create regional administrators"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email_or_phone', 'scope_code', 'password']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    "error": f"Field '{field}' is required"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        email_or_phone = request.data['email_or_phone']
        scope_code = request.data['scope_code']
        password = request.data['password']
        
        # Lookup the organizational node
        try:
            scope_node = OrganizationNode.objects.get(code=scope_code, is_active=True)
        except OrganizationNode.DoesNotExist:
            return Response({
                "error": f"Organization node with code '{scope_code}' does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate username
        username = f"{first_name.lower()}.{last_name.lower()}"
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Determine if email or phone
        user_data = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'admin_scope': scope_node,
            'is_staff': True,
            'is_superuser': False
        }
        
        if '@' in email_or_phone:
            if User.objects.filter(email=email_or_phone).exists():
                return Response({
                    "error": "A user with this email already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            user_data['email'] = email_or_phone
            user_data['phone_number'] = None
        else:
            if User.objects.filter(phone_number=email_or_phone).exists():
                return Response({
                    "error": "A user with this phone number already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            user_data['phone_number'] = email_or_phone
            user_data['email'] = ''
        
        # Create the regional admin
        user = User.objects.create_user(**user_data)
        
        return Response({
            "message": f"Regional admin created successfully for {scope_node.name}",
            "admin": {
                "username": user.username,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "scope": scope_node.code,
                "scopeName": scope_node.name,
                "scopeDepth": scope_node.depth
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """User login endpoint - Login with email/phone and password"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Determine role and scope
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
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "firstName": user.first_name,
                "lastName": user.last_name,
                "role": role,
                "scope": scope,
                "scopeName": scope_name,
                "homeAltar": user.home_altar.name if user.home_altar else None
            }
        }, status=status.HTTP_200_OK)


class MemberCreateView(generics.CreateAPIView):
    """Create new church members (filtered by organizational scope)"""
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated, HasOrganizationalScope, CanManageMembers]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate that the altar is within admin's scope
        altar = serializer.validated_data.get('home_altar')
        if not request.user.is_superuser and not request.user.can_manage_altar(altar):
            return Response({
                "error": (
                    f"You don't have permission to create members for '{altar.name}'. "
                    f"You can only manage altars within your organizational scope."
                )
            }, status=status.HTTP_403_FORBIDDEN)

        member = serializer.save()

        return Response({
            "message": "Member created successfully",
            "member": MemberSerializer(member).data
        }, status=status.HTTP_201_CREATED)


class AltarListView(generics.ListAPIView):
    """List all available altars within admin's organizational scope"""
    permission_classes = [IsAuthenticated, HasOrganizationalScope]

    def get(self, request, *args, **kwargs):
        # Superusers see all altars
        if request.user.is_superuser:
            altars = Altar.objects.filter(is_active=True).values('id', 'name', 'city')
        else:
            # Regular admins only see altars within their scope
            altars = request.user.get_accessible_altars().values('id', 'name', 'city')

        return Response({
            "count": altars.count(),
            "altars": list(altars)
        }, status=status.HTTP_200_OK)


# TODO: Re-enable after creating Guest model
# class GuestCreateView(generics.CreateAPIView):
#     """Onboard new guests/visitors (filtered by organizational scope)"""
#     queryset = Guest.objects.all()
#     serializer_class = GuestSerializer
#     permission_classes = [IsAuthenticated, HasOrganizationalScope, CanManageGuests]
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         guest = serializer.save()
#
#         return Response({
#             "message": "Guest onboarded successfully",
#             "guest": GuestSerializer(guest).data
#         }, status=status.HTTP_201_CREATED)


# TODO: Re-enable after creating MemberTransferHistory model
# class MemberTransferView(APIView):
#     """Transfer member to another altar or deactivate them (filtered by organizational scope)"""
#     permission_classes = [IsAuthenticated, HasOrganizationalScope, CanTransferMembers]
#
#     @transaction.atomic
#     def post(self, request):
#         ...
#         # Implementation commented out - requires MemberTransferHistory model


class LogoutView(APIView):
    """Logout endpoint - blacklist the refresh token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Invalid token or token already blacklisted"},
                status=status.HTTP_400_BAD_REQUEST
            )


class MemberListView(generics.ListAPIView):
    """List all active members for attendance marking (filtered by organizational scope)"""
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated, HasOrganizationalScope]

    def get_queryset(self):
        """Get active members within admin's organizational scope"""
        queryset = Member.objects.filter(is_active=True).select_related('home_altar')

        # Superusers see all members
        if self.request.user.is_superuser:
            pass  # No filtering needed
        else:
            # Regular admins only see members within their scope
            accessible_altars = self.request.user.get_accessible_altars()
            queryset = queryset.filter(home_altar__in=accessible_altars)

        # Optional filter by altar
        altar_name = self.request.query_params.get('altar', None)
        if altar_name:
            queryset = queryset.filter(home_altar__name=altar_name)

        return queryset.order_by('full_name')


class RegionalDashboardView(APIView):
    """
    Regional dashboard showing aggregated metrics for all sub-regions and altars.
    For Regional Superadmins (e.g., Senior Deputy Archbishop of Central Region)
    """
    permission_classes = [IsAuthenticated, HasOrganizationalScope]

    def get(self, request):
        user = request.user
        
        # Get the organizational scope (e.g., CENTRAL region)
        if user.is_superuser:
            # Global superadmin sees all regions
            root_nodes = OrganizationNode.objects.filter(parent__isnull=False, depth=1, is_active=True)
            scope_name = "All Regions"
        elif user.admin_scope:
            # Regional admin sees their region and sub-regions
            root_nodes = [user.admin_scope]
            scope_name = user.admin_scope.name
        else:
            return Response({
                "error": "No organizational scope assigned"
            }, status=status.HTTP_403_FORBIDDEN)

        # Build regional report
        regional_data = []
        
        for region in root_nodes:
            # Get all descendant nodes (sub-regions) under this region
            sub_regions = region.get_descendants(include_self=False).filter(is_active=True)
            
            # Get all altars under this region
            altars_in_region = Altar.objects.filter(
                parent_node__in=region.get_descendants(include_self=True),
                is_active=True
            )
            
            # Get all members under this region's altars
            members_in_region = Member.objects.filter(
                home_altar__in=altars_in_region,
                is_active=True
            )
            
            # Calculate metrics
            total_altars = altars_in_region.count()
            total_members = members_in_region.count()
            total_sub_regions = sub_regions.count()
            
            # Gender breakdown
            male_count = members_in_region.filter(gender='M').count()
            female_count = members_in_region.filter(gender='F').count()
            
            # Sub-region breakdown
            sub_region_breakdown = []
            for sub_region in sub_regions:
                altars_in_sub = Altar.objects.filter(
                    parent_node=sub_region,
                    is_active=True
                )
                members_in_sub = Member.objects.filter(
                    home_altar__in=altars_in_sub,
                    is_active=True
                )
                
                sub_region_breakdown.append({
                    "name": sub_region.name,
                    "code": sub_region.code,
                    "total_altars": altars_in_sub.count(),
                    "total_members": members_in_sub.count(),
                    "altars": [
                        {
                            "name": altar.name,
                            "city": altar.city,
                            "member_count": Member.objects.filter(
                                home_altar=altar,
                                is_active=True
                            ).count()
                        }
                        for altar in altars_in_sub
                    ]
                })
            
            regional_data.append({
                "region": {
                    "name": region.name,
                    "code": region.code,
                    "leader": region.current_leader.get_full_name() if region.current_leader else "Not Assigned"
                },
                "summary": {
                    "total_sub_regions": total_sub_regions,
                    "total_altars": total_altars,
                    "total_members": total_members,
                    "male_members": male_count,
                    "female_members": female_count,
                    # TODO: Add these after implementing Guest and AttendanceLog models
                    "total_guests": 0,
                    "total_present_today": 0,
                    "total_absent_today": 0
                },
                "sub_regions": sub_region_breakdown
            })
        
        return Response({
            "scope": scope_name,
            "report_date": timezone.now().date(),
            "regions": regional_data
        }, status=status.HTTP_200_OK)


class AltarDashboardView(APIView):
    """
    Individual altar dashboard showing detailed metrics for one altar.
    For Altar Admins
    """
    permission_classes = [IsAuthenticated, HasOrganizationalScope]

    def get(self, request):
        user = request.user
        
        # Get altar from query params or user's scope
        altar_name = request.query_params.get('altar')
        
        if altar_name:
            # Fetch specific altar
            try:
                altar = Altar.objects.get(name=altar_name, is_active=True)
            except Altar.DoesNotExist:
                return Response({
                    "error": f"Altar '{altar_name}' not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check permission
            if not user.is_superuser and not user.can_manage_altar(altar):
                return Response({
                    "error": "You don't have permission to view this altar's dashboard"
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            # Get user's primary altar if they're an altar admin
            accessible_altars = user.get_accessible_altars()
            if accessible_altars.count() == 0:
                return Response({
                    "error": "No altars accessible"
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Default to first accessible altar
            altar = accessible_altars.first()
        
        # Get members for this altar
        members = Member.objects.filter(home_altar=altar, is_active=True)
        
        # Calculate metrics
        total_members = members.count()
        male_count = members.filter(gender='M').count()
        female_count = members.filter(gender='F').count()
        
        # Department breakdown
        departments = members.values('serving_department').annotate(
            count=models.Count('id')
        ).order_by('-count')
        
        return Response({
            "altar": {
                "name": altar.name,
                "code": altar.code,
                "city": altar.city,
                "pastor": altar.pastor.get_full_name() if altar.pastor else "Not Assigned",
                "parent_region": altar.parent_node.name if altar.parent_node else None
            },
            "summary": {
                "total_members": total_members,
                "male_members": male_count,
                "female_members": female_count,
                # TODO: Add these after implementing Guest and AttendanceLog models
                "total_guests": 0,
                "present_today": 0,
                "absent_today": 0,
                "attendance_rate": 0.0
            },
            "departments": list(departments),
            "recent_members": [
                {
                    "id": m.id,
                    "full_name": m.full_name,
                    "phone_number": m.phone_number,
                    "gender": m.gender,
                    "serving_department": m.serving_department,
                    "membership_date": m.membership_date
                }
                for m in members.order_by('-created_at')[:10]
            ]
        }, status=status.HTTP_200_OK)


# TODO: Re-enable after creating AttendanceLog model
# class BulkAttendanceView(APIView):
#     """Record attendance for multiple members at once (filtered by organizational scope)"""
#     ...
#     # Implementation commented out - requires AttendanceLog model
