from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.models import User, Member, OrganizationUnit
from .serializers import RegisterSerializer, UserSerializer, MemberSerializer


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
