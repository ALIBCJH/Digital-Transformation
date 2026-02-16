from rest_framework import serializers
from core.models import User, Member, Guest, OrganizationUnit


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    organizational_unit = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="Name of the organizational unit this admin will manage (region, sub-region, or altar)"
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'phone_number', 'first_name', 'last_name', 'organizational_unit'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def validate_organizational_unit(self, value):
        """Look up the organizational unit by name if provided"""
        if value:
            try:
                org_unit = OrganizationUnit.objects.get(
                    name=value,
                    level__in=['REGION', 'SUB_REGION', 'ALTAR']
                )
                return org_unit
            except OrganizationUnit.DoesNotExist:
                raise serializers.ValidationError(
                    f"Organizational unit '{value}' does not exist. "
                    f"Must be a valid region, sub-region, or altar name."
                )
        return None

    def create(self, validated_data):
        validated_data.pop('password2')
        org_unit = validated_data.pop('organizational_unit', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            organizational_unit=org_unit,
            is_staff=True,
            is_superuser=False  # Regular admins are not superusers
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    organizational_unit_name = serializers.CharField(source='organizational_unit.name', read_only=True)
    organizational_unit_level = serializers.CharField(source='organizational_unit.level', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_superuser', 'organizational_unit_name', 'organizational_unit_level'
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


class GuestSerializer(serializers.ModelSerializer):
    """Serializer for guest onboarding"""

    class Meta:
        model = Guest
        fields = [
            'id',
            'full_name',
            'phone_number',
            'gender',
            'visiting_from',  # place of origin
            'first_visit_date',
            'visit_count',
            'created_at'
        ]
        read_only_fields = ['id', 'first_visit_date', 'visit_count', 'created_at']

    def validate_phone_number(self, value):
        """Ensure the phone number is valid if provided"""
        if value:
            # Remove common phone number formatting characters
            cleaned = value.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if not cleaned.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits, spaces, hyphens, or plus sign.")
        return value


class MemberTransferSerializer(serializers.Serializer):
    """Serializer for member transfer/offboarding"""
    member_id = serializers.IntegerField(help_text="ID of the member to transfer")
    to_altar = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="Name of destination altar (leave empty to deactivate member)"
    )
    transfer_reason = serializers.ChoiceField(
        choices=['JOB_TRANSFER', 'RELOCATION', 'FAMILY_REASONS', 'PERSONAL_CHOICE', 'OTHER'],
        default='JOB_TRANSFER'
    )
    notes = serializers.CharField(required=False, allow_blank=True, help_text="Additional notes about the transfer")

    def validate_member_id(self, value):
        """Check if member exists"""
        try:
            member = Member.objects.get(id=value)
            if not member.is_active:
                raise serializers.ValidationError("Member is already inactive.")
            return value
        except Member.DoesNotExist:
            raise serializers.ValidationError("Member not found.")

    def validate_to_altar(self, value):
        """Look up the destination altar if provided"""
        if value:
            try:
                altar = OrganizationUnit.objects.get(name=value, level='ALTAR')
                return altar
            except OrganizationUnit.DoesNotExist:
                raise serializers.ValidationError(f"Altar '{value}' does not exist.")
        return None


class MemberListSerializer(serializers.ModelSerializer):
    """Simplified serializer for member list display"""
    home_altar_name = serializers.CharField(source='home_altar.name', read_only=True)

    class Meta:
        model = Member
        fields = [
            'id',
            'full_name',
            'phone_number',
            'gender',
            'serving_department',
            'home_altar_name',
            'is_active'
        ]


class AttendanceRecordSerializer(serializers.Serializer):
    """Serializer for a single attendance record"""
    member_id = serializers.IntegerField()
    attended = serializers.BooleanField()


class BulkAttendanceSerializer(serializers.Serializer):
    """Serializer for bulk attendance recording"""
    altar = serializers.CharField(help_text="Name of the altar where service was held")
    service_date = serializers.DateField(help_text="Date of the service (YYYY-MM-DD)")
    service_type = serializers.ChoiceField(
        choices=['SUNDAY', 'MIDWEEK', 'SPECIAL'],
        default='SUNDAY',
        help_text="Type of service"
    )
    attendance_records = serializers.ListField(
        child=AttendanceRecordSerializer(),
        help_text="List of member attendance records"
    )

    def validate_altar(self, value):
        """Validate that the altar exists"""
        try:
            altar = OrganizationUnit.objects.get(name=value, level='ALTAR')
            return altar
        except OrganizationUnit.DoesNotExist:
            raise serializers.ValidationError(f"Altar '{value}' does not exist.")

    def validate_attendance_records(self, value):
        """Validate that all member IDs exist and are active"""
        member_ids = [record['member_id'] for record in value]
        existing_members = Member.objects.filter(id__in=member_ids, is_active=True).values_list('id', flat=True)

        invalid_ids = set(member_ids) - set(existing_members)
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid or inactive member IDs: {list(invalid_ids)}")

        return value
