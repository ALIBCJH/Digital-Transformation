from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from core.models import User, Member, Guest, OrganizationUnit, MemberTransferHistory, AttendanceLog
from .serializers import (
    RegisterSerializer, UserSerializer, MemberSerializer, 
    GuestSerializer, MemberTransferSerializer, MemberListSerializer,
    BulkAttendanceSerializer
)


class RegisterView(generics.CreateAPIView):
    """Admin user registration endpoint"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "message": "Admin user created successfully",
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class MemberCreateView(generics.CreateAPIView):
    """Create new church members"""
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        
        return Response({
            "message": "Member created successfully",
            "member": MemberSerializer(member).data
        }, status=status.HTTP_201_CREATED)


class AltarListView(generics.ListAPIView):
    """List all available altars"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        altars = OrganizationUnit.objects.filter(level='ALTAR', is_active=True).values('id', 'name')
        return Response({
            "count": altars.count(),
            "altars": list(altars)
        }, status=status.HTTP_200_OK)


class GuestCreateView(generics.CreateAPIView):
    """Onboard new guests/visitors"""
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        guest = serializer.save()
        
        return Response({
            "message": "Guest onboarded successfully",
            "guest": GuestSerializer(guest).data
        }, status=status.HTTP_201_CREATED)


class MemberTransferView(APIView):
    """Transfer member to another altar or deactivate them"""
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = MemberTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        member_id = serializer.validated_data['member_id']
        to_altar = serializer.validated_data.get('to_altar')
        transfer_reason = serializer.validated_data['transfer_reason']
        notes = serializer.validated_data.get('notes', '')
        
        # Get the member
        member = Member.objects.get(id=member_id)
        from_altar = member.home_altar
        
        # Create transfer history record
        transfer = MemberTransferHistory.objects.create(
            member=member,
            from_altar=from_altar,
            to_altar=to_altar,
            transfer_reason=transfer_reason,
            notes=notes,
            processed_by=request.user
        )
        
        # Update member
        if to_altar:
            # Transfer to new altar
            member.home_altar = to_altar
            member.save()
            message = f"Member {member.full_name} transferred from {from_altar.name} to {to_altar.name}"
        else:
            # Deactivate member (leaving/offboarding)
            member.is_active = False
            member.save()
            message = f"Member {member.full_name} has been deactivated and offboarded from {from_altar.name}"
        
        return Response({
            "message": message,
            "transfer": {
                "id": transfer.id,
                "member": member.full_name,
                "from_altar": from_altar.name,
                "to_altar": to_altar.name if to_altar else "Deactivated",
                "transfer_reason": transfer_reason,
                "transfer_date": transfer.transfer_date,
                "processed_by": request.user.username
            }
        }, status=status.HTTP_200_OK)


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
        except Exception as e:
            return Response(
                {"error": "Invalid token or token already blacklisted"},
                status=status.HTTP_400_BAD_REQUEST
            )


class MemberListView(generics.ListAPIView):
    """List all active members for attendance marking"""
    serializer_class = MemberListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get active members, optionally filtered by altar"""
        queryset = Member.objects.filter(is_active=True).select_related('home_altar')
        
        # Optional filter by altar
        altar_name = self.request.query_params.get('altar', None)
        if altar_name:
            queryset = queryset.filter(home_altar__name=altar_name)
        
        return queryset.order_by('full_name')


class BulkAttendanceView(APIView):
    """Record attendance for multiple members at once"""
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        altar = serializer.validated_data['altar']
        service_date = serializer.validated_data['service_date']
        service_type = serializer.validated_data['service_type']
        attendance_records = serializer.validated_data['attendance_records']
        
        # Get the organizational hierarchy for denormalization
        # Navigate up the hierarchy to get all parent levels
        current_unit = altar
        hierarchy = {}
        
        while current_unit:
            hierarchy[current_unit.level] = current_unit
            current_unit = current_unit.parent
        
        # Extract hierarchy levels (all required for AttendanceLog)
        sub_region = hierarchy.get('SUB_REGION')
        region = hierarchy.get('REGION')
        country = hierarchy.get('COUNTRY')
        continent = hierarchy.get('CONTINENT')
        
        # Validate that we have all required hierarchy levels
        if not all([sub_region, region, country, continent]):
            return Response(
                {
                    'error': f'Incomplete organizational hierarchy for altar "{altar.name}". '
                             f'Missing: {", ".join([level for level in ["CONTINENT", "COUNTRY", "REGION", "SUB_REGION"] if level not in hierarchy])}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare attendance logs
        attendance_logs = []
        members_present = []
        
        for record in attendance_records:
            if record['attended']:
                member = Member.objects.get(id=record['member_id'])
                members_present.append(member.full_name)
                
                attendance_logs.append(
                    AttendanceLog(
                        member=member,
                        altar=altar,
                        sub_region=sub_region,
                        region=region,
                        country=country,
                        continent=continent,
                        service_date=service_date,
                        service_type=service_type,
                        recorded_by=request.user
                    )
                )
        
        # Bulk create attendance records
        if attendance_logs:
            AttendanceLog.objects.bulk_create(
                attendance_logs,
                ignore_conflicts=True  # Ignore if record already exists
            )
        
        return Response({
            "message": f"Attendance recorded successfully for {len(members_present)} members",
            "altar": altar.name,
            "service_date": service_date,
            "service_type": service_type,
            "members_present_count": len(members_present),
            "total_records_processed": len(attendance_records),
            "members_present": members_present[:10]  # Show first 10 names
        }, status=status.HTTP_201_CREATED)
