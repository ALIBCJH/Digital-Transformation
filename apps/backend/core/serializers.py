from rest_framework import serializers
from django.contrib.auth import authenticate
from core.models import User, Member, Altar, OrganizationNode


class RegisterSerializer(serializers.ModelSerializer):
    """Simplified registration: first_name, last_name, email_or_phone, altar, password"""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    email_or_phone = serializers.CharField(
        write_only=True,
        help_text="Email address or phone number for login"
    )
    altar = serializers.CharField(
        help_text="Name of the altar you belong to"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email_or_phone', 'altar', 'password', 'password2']

    def validate_email_or_phone(self, value):
        """Check if it's email or phone and validate uniqueness"""
        # Simple check: if contains @, treat as email, otherwise as phone
        if '@' in value:
            # It's an email
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
            return {'type': 'email', 'value': value}
        else:
            # It's a phone number
            if User.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("A user with this phone number already exists.")
            return {'type': 'phone', 'value': value}

    def validate_altar(self, value):
        """Look up the altar by name"""
        try:
            altar = Altar.objects.get(name=value, is_active=True)
            return altar
        except Altar.DoesNotExist:
            raise serializers.ValidationError(
                f"Altar '{value}' does not exist. Please provide a valid altar name."
            )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})

        # Validate required fields
        if not attrs.get('first_name'):
            raise serializers.ValidationError({"first_name": "First name is required"})
        if not attrs.get('last_name'):
            raise serializers.ValidationError({"last_name": "Last name is required"})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        email_or_phone = validated_data.pop('email_or_phone')
        altar = validated_data.pop('altar')

        # Generate username from first and last name
        username = f"{validated_data['first_name'].lower()}.{validated_data['last_name'].lower()}"
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create user based on whether email or phone was provided
        # All users are admins managing their altar's scope
        user_data = {
            'username': username,
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'password': validated_data['password'],
            'home_altar': altar,
            'admin_scope': altar.parent_node,  # Admin manages the node containing their altar
            'is_staff': True,  # All users are admins
            'is_superuser': False
        }

        if email_or_phone['type'] == 'email':
            user_data['email'] = email_or_phone['value']
            user_data['phone_number'] = None  # Use None instead of empty string
        else:
            user_data['phone_number'] = email_or_phone['value']
            user_data['email'] = ''  # Email can be empty string (AbstractUser default)

        user = User.objects.create_user(**user_data)
        return user


class SuperAdminRegisterSerializer(serializers.Serializer):
    """
    Serializer for creating regional/sub-regional superadmins.
    Creates admins with organizational scope (region or sub-region).
    """
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    admin_scope = serializers.CharField(
        help_text="Organization code (e.g., CENTRAL, NYERI)"
    )

    def validate(self, attrs):
        """Validate that passwords match and at least one of email/phone is provided"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        email = attrs.get('email', '').strip()
        phone = attrs.get('phone_number', '').strip()

        if not email and not phone:
            raise serializers.ValidationError(
                "Either email or phone_number must be provided"
            )

        # Validate email uniqueness if provided
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists"})

        # Validate phone uniqueness if provided
        if phone and User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError(
                {"phone_number": "A user with this phone number already exists"}
            )

        # Validate admin_scope exists
        try:
            scope_node = OrganizationNode.objects.get(
                code=attrs['admin_scope'],
                is_active=True
            )
            attrs['scope_node'] = scope_node
        except OrganizationNode.DoesNotExist:
            raise serializers.ValidationError({
                "admin_scope": f"Organization node with code '{attrs['admin_scope']}' does not exist"
            })

        return attrs

    def create(self, validated_data):
        """Create the superadmin user"""
        # Generate username
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        username = f"{first_name.lower()}.{last_name.lower()}"
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Prepare user data
        user_data = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'admin_scope': validated_data['scope_node'],
            'is_staff': True,
            'is_superuser': False  # Regional admins are NOT global superusers
        }

        email = validated_data.get('email', '').strip()
        phone = validated_data.get('phone_number', '').strip()

        if email:
            user_data['email'] = email
            user_data['phone_number'] = phone if phone else None
        else:
            user_data['phone_number'] = phone
            user_data['email'] = ''

        user = User.objects.create_user(password=validated_data['password'], **user_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Login with email or phone number and password"""
    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        password = attrs.get('password')

        if not email_or_phone or not password:
            raise serializers.ValidationError("Both email/phone and password are required")

        # Determine if it's email or phone
        if '@' in email_or_phone:
            # Try to find user by email
            try:
                user = User.objects.get(email=email_or_phone)
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")
        else:
            # Try to find user by phone
            try:
                user = User.objects.get(phone_number=email_or_phone)
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")

        # Authenticate using username
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    admin_scope_name = serializers.CharField(source='admin_scope.name', read_only=True)
    admin_scope_code = serializers.CharField(source='admin_scope.code', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_superuser', 'admin_scope_name', 'admin_scope_code'
        ]


class MemberSerializer(serializers.ModelSerializer):
    # Accept altar name as string for input, return it for output
    home_altar = serializers.CharField()

    class Meta:
        model = Member
        fields = [
            'id',
            'full_name',
            'phone_number',
            'email',
            'gender',
            'membership_date',
            'date_of_birth',
            'is_active',
            'home_altar',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'membership_date']

    def validate_home_altar(self, value):
        """Look up the altar by name"""
        try:
            altar = Altar.objects.get(name=value, is_active=True)
            return altar
        except Altar.DoesNotExist:
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


# TODO: Re-enable after creating Guest model
# class GuestSerializer(serializers.ModelSerializer):
#     """Serializer for guest onboarding"""
#     ...


class MemberTransferSerializer(serializers.Serializer):
    """Serializer for member transfer/offboarding"""
    member_id = serializers.IntegerField(required=True)
    to_altar_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text='Altar ID to transfer to. Leave empty/null to offboard (deactivate) the member.'
    )
    reason = serializers.ChoiceField(
        choices=[
            ('job_transfer', 'Job Transfer'),
            ('relocation', 'Relocation'),
            ('family_reasons', 'Family Reasons'),
            ('personal_choice', 'Personal Choice'),
            ('offboarding', 'Offboarding/Leaving'),
            ('other', 'Other'),
        ],
        default='other'
    )
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_member_id(self, value):
        """Validate that the member exists and is active"""
        try:
            member = Member.objects.get(id=value, is_active=True)
            return member
        except Member.DoesNotExist:
            raise serializers.ValidationError(f"Active member with ID {value} does not exist")

    def validate_to_altar_id(self, value):
        """Validate that the altar exists if provided"""
        if value is None:
            return None
        try:
            altar = Altar.objects.get(id=value, is_active=True)
            return altar
        except Altar.DoesNotExist:
            raise serializers.ValidationError(f"Active altar with ID {value} does not exist")


# TODO: Re-enable after creating AttendanceLog model
class AttendanceRecordSerializer(serializers.Serializer):
    """Serializer for a single attendance record"""
    member_id = serializers.IntegerField()
    is_present = serializers.BooleanField()


class BulkAttendanceSerializer(serializers.Serializer):
    """
    Serializer for bulk attendance recording.
    Accepts altar_id, service_date, service_type, and list of member attendance.
    """
    altar_id = serializers.IntegerField()
    service_date = serializers.DateField()
    service_type = serializers.ChoiceField(
        choices=[
            ('sunday_service', 'Sunday Service'),
            ('midweek_service', 'Midweek Service'),
            ('special_service', 'Special Service'),
            ('prayer_meeting', 'Prayer Meeting'),
            ('other', 'Other'),
        ],
        default='sunday_service'
    )
    attendance = serializers.ListField(
        child=AttendanceRecordSerializer(),
        help_text="List of member IDs and their attendance status"
    )

    def validate_altar_id(self, value):
        """Validate that the altar exists"""
        try:
            from core.models import Altar
            altar = Altar.objects.get(id=value, is_active=True)
            return altar
        except Altar.DoesNotExist:
            raise serializers.ValidationError(f"Altar with ID {value} does not exist")

    def validate_attendance(self, value):
        """Validate that all member IDs exist"""
        from core.models import Member
        member_ids = [record['member_id'] for record in value]
        
        existing_members = Member.objects.filter(
            id__in=member_ids,
            is_active=True
        ).values_list('id', flat=True)
        
        invalid_ids = set(member_ids) - set(existing_members)
        if invalid_ids:
            raise serializers.ValidationError(
                f"Invalid member IDs: {list(invalid_ids)}"
            )
        
        return value
