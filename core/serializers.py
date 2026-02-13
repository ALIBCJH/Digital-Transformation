from rest_framework import serializers
from core.models import User
from core.models import Member , OrganizationUnit

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'phone_number', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=True,
            is_superuser=True
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']

class MemberSerializer(serializers.ModelSerializer):
    # Accept altar name as string for input, return it for output
    home_altar = serializers.CharField()

    class Meta:
        model = Member
        fields = [
            'id',
            'full_name',
            'phone_number',
            'gender',
            'serving_department',
            'membership_date',
            'date_of_birth',
            'is_active',
            'home_altar',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_home_altar(self, value):
        """Look up the altar by name and validate it's an ALTAR level unit"""
        try:
            altar = OrganizationUnit.objects.get(name=value, level='ALTAR')
            return altar
        except OrganizationUnit.DoesNotExist:
            raise serializers.ValidationError(f"Altar '{value}' does not exist. Please provide a valid altar name.")
    
    def validate_phone_number(self, value):
        """Ensure the phone number is valid"""
        if value:
            # Remove common phone number formatting characters
            cleaned = value.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if not cleaned.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits, spaces, hyphens, or plus sign.")
        return value
    
    def to_representation(self, instance):
        """Return altar name instead of ID when reading"""
        representation = super().to_representation(instance)
        representation['home_altar'] = instance.home_altar.name if instance.home_altar else None
        return representation