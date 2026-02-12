from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.models import User
from .serializers import RegisterSerializer, UserSerializer


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
