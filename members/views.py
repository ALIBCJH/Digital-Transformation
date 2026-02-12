from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from core.models import Member
from core.serializers import MemberSerializer


class MemberCreateView(generics.CreateAPIView):
    """Endpoint for creating a new member"""
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        return Response({
            "message": "Member created successfully",
            "member": MemberSerializer(member).data
        }, status=status.HTTP_201_CREATED)


class MemberListView(generics.ListAPIView):
    """List all members (admin only, with filters)"""
    serializer_class = MemberSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Member.objects.select_related('home_altar').all()

        # APPLY FILTERS
        altar_id = self.request.query_params.get('altar_id')
        gender = self.request.query_params.get('gender')
        is_active = self.request.query_params.get('is_active')

        if altar_id:
            queryset = queryset.filter(home_altar_id=altar_id)
        if gender:
            queryset = queryset.filter(gender=gender)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.order_by('-created_at')


class MemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a member (admin only)"""
    queryset = Member.objects.select_related('home_altar').all()
    serializer_class = MemberSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'