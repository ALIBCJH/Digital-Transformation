from rest_framework import serializers
from core.models import User
from core.models import Member , OrganizationUnit

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']

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
    # Read-only fields for display
    home_altar_name = serializers.CharField(source='home_altar.name', read_only=True)
    age = serializers.IntegerField(read_only=True, help_text="Calculated from date_of_birth")
    department = serializers.CharField(source='home_altar.name', read_only=True, help_text="Department/Altar name")

    class Meta:
        model = Member
        fields = [
            'id',
            'full_name',           # Name
            'gender',              # Gender
            'date_of_birth',       # For age calculation
            'age',                 # Age (calculated)
            'phone_number',        # Phone number
            'home_altar',          # Department (FK ID)
            'home_altar_name',     # Department name (read-only)
            'department',          # Alias for home_altar_name
            'membership_date',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'age', 'home_altar_name', 'department', 'created_at']
    
    def validate_home_altar(self, value):
        """Ensure the home_altar is an ALTAR level unit (Department)"""
        if value.level != 'ALTAR':
            raise serializers.ValidationError("Members must be assigned to an ALTAR (Department), not a REGION or COUNTRY.")
        return value
    
    def validate_phone_number(self, value):
        """Ensure the phone number is valid"""
        if value:
            # Remove common phone number formatting characters
            cleaned = value.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if not cleaned.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits, spaces, hyphens, or plus sign.")
        return value