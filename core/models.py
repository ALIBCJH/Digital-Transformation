from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ============================================
# ENUMS
# ============================================

class UnitLevel(models.TextChoices):
    """Organization hierarchy levels"""
    CONTINENT = 'CONTINENT', 'Continent'
    COUNTRY = 'COUNTRY', 'Country'
    REGION = 'REGION', 'Region'
    SUB_REGION = 'SUB_REGION', 'Sub-Region'
    ALTAR = 'ALTAR', 'Altar'


class Gender(models.TextChoices):
    """Gender options"""
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    OTHER = 'OTHER', 'Other'


class ServiceType(models.TextChoices):
    """Service types"""
    SUNDAY = 'SUNDAY', 'Sunday Service'
    MIDWEEK = 'MIDWEEK', 'Midweek Service'
    SPECIAL = 'SPECIAL', 'Special Event'


class LeadershipTitle(models.TextChoices):
    """Leadership titles"""
    PRESIDING_ARCHBISHOP = 'PRESIDING_ARCHBISHOP', 'Presiding Archbishop'
    NATIONAL_ARCHBISHOP = 'NATIONAL_ARCHBISHOP', 'National Archbishop'
    SENIOR_DEPUTY_ARCHBISHOP = 'SENIOR_DEPUTY_ARCHBISHOP', 'Senior Deputy Archbishop'
    BISHOP = 'BISHOP', 'Bishop'
    DEPUTY_ARCHBISHOP = 'DEPUTY_ARCHBISHOP', 'Deputy Archbishop'
    OVERSEER = 'OVERSEER', 'Overseer'
    PASTOR = 'PASTOR', 'Pastor'
    MEMBER = 'MEMBER', 'Member'


class LeadershipEndReason(models.TextChoices):
    """Reasons for ending leadership"""
    TRANSFERRED = 'TRANSFERRED', 'Transferred'
    PROMOTED = 'PROMOTED', 'Promoted'
    RETIRED = 'RETIRED', 'Retired'
    RESIGNED = 'RESIGNED', 'Resigned'
    DECEASED = 'DECEASED', 'Deceased'
    REMOVED = 'REMOVED', 'Removed'
    OTHER = 'OTHER', 'Other'


# ============================================
# ORGANIZATION STRUCTURE
# ============================================

class OrganizationUnit(models.Model):
    """Hierarchical church structure: Continent → Country → Region → Sub-Region → Altar"""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=UnitLevel.choices)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    current_leader = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='currently_leading'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organization_units'
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['parent']),
            models.Index(fields=['level', 'parent']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.level})"


# ============================================
# USERS & AUTHENTICATION
# ============================================

class User(AbstractUser):
    """Extended user model for authentication and leadership"""
    phone_number = models.CharField(max_length=20, unique=True)
    home_altar = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.PROTECT,
        related_name='home_members',
        null=True,
        blank=True
    )
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Fix for Django auth clash - override groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='core_users',
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_users',
        related_query_name='core_user',
    )

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['email']),
            models.Index(fields=['home_altar']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"


class OTPCode(models.Model):
    """One-time password codes for SMS verification"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20)  # 'activation', 'login', 'reset'
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = 'otp_codes'
        indexes = [
            models.Index(fields=['user', 'purpose']),
            models.Index(fields=['code']),
        ]

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at


# ============================================
# LEADERSHIP TRACKING
# ============================================

class LeadershipHistory(models.Model):
    """Track all leadership assignments and changes"""
    organization_unit = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.CASCADE,
        related_name='leadership_history'
    )
    leader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leadership_positions'
    )
    leadership_title = models.CharField(max_length=50, choices=LeadershipTitle.choices)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    end_reason = models.CharField(
        max_length=20,
        choices=LeadershipEndReason.choices,
        null=True,
        blank=True
    )
    transferred_to = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transferred_leaders'
    )
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='leadership_assignments_made'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leadership_history'
        indexes = [
            models.Index(fields=['organization_unit', 'end_date']),
            models.Index(fields=['leader']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return f"{self.leader.get_full_name()} - {self.organization_unit.name} ({self.leadership_title})"


# ============================================
# MEMBERS
# ============================================

class Member(models.Model):
    """Church members"""
    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=255, help_text="Full name of the member")
    phone_number = models.CharField(max_length=20, unique=True, help_text="Contact phone number")
    gender = models.CharField(max_length=10, choices=Gender.choices, help_text="Gender of the member")
    serving_department = models.CharField(max_length=255, help_text="Department where the member serves", null=True, blank=True)
    membership_date = models.DateField(default=timezone.now)
    date_of_birth = models.DateField(null=True, blank=True, help_text="Date of birth for age calculation")
    is_active = models.BooleanField(default=True)
    home_altar = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.PROTECT,
        related_name='members',
        limit_choices_to={'level': UnitLevel.ALTAR},
        help_text="Home altar the member belongs to"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'members'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['home_altar']),
            models.Index(fields=['is_active']),
            models.Index(fields=['home_altar', 'is_active']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"


# ============================================
# GUESTS
# ============================================

class Guest(models.Model):
    """Church guests/visitors"""
    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
    visiting_from = models.CharField(max_length=255, null=True, blank=True)
    first_visit_date = models.DateField(default=timezone.now)
    last_visit_date = models.DateField(default=timezone.now)
    visit_count = models.IntegerField(default=1)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'guests'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['first_visit_date']),
        ]

    def __str__(self):
        return f"{self.full_name} (Guest)"


# ============================================
# ATTENDANCE
# ============================================

class AttendanceLog(models.Model):
    """Attendance records with denormalized fields for fast reporting"""
    id = models.BigAutoField(primary_key=True)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attendance_logs'
    )
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attendance_logs'
    )
    # Denormalized hierarchy for fast reporting
    altar = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.CASCADE,
        related_name='altar_attendance_logs'
    )
    sub_region = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.CASCADE,
        related_name='sub_region_attendance_logs'
    )
    region = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.CASCADE,
        related_name='region_attendance_logs'
    )
    country = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.CASCADE,
        related_name='country_attendance_logs'
    )
    continent = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.CASCADE,
        related_name='continent_attendance_logs'
    )
    service_date = models.DateField()
    service_type = models.CharField(
        max_length=20,
        choices=ServiceType.choices,
        default=ServiceType.SUNDAY
    )
    timestamp = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_attendances'
    )

    class Meta:
        db_table = 'attendance_logs'
        indexes = [
            models.Index(fields=['service_date', 'country']),
            models.Index(fields=['service_date', 'continent']),
            models.Index(fields=['altar', 'service_date']),
            models.Index(fields=['sub_region', 'service_date']),
            models.Index(fields=['region', 'service_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'service_date'],
                name='unique_member_service_date',
                condition=models.Q(member__isnull=False)
            ),
        ]

    def __str__(self):
        person = self.member.full_name if self.member else self.guest.full_name
        return f"{person} - {self.service_date}"


# ============================================
# QUOTAS & MONITORING
# ============================================

class DataEntryQuota(models.Model):
    """Daily quotas for data entry to prevent spam"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    attendance_records_created = models.IntegerField(default=0)
    guests_registered = models.IntegerField(default=0)

    MAX_ATTENDANCE_PER_DAY = 500
    MAX_GUESTS_PER_DAY = 100

    class Meta:
        db_table = 'data_entry_quotas'
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def can_mark_attendance(self):
        return self.attendance_records_created < self.MAX_ATTENDANCE_PER_DAY

    def can_register_guest(self):
        return self.guests_registered < self.MAX_GUESTS_PER_DAY


class AltarStatistics(models.Model):
    """Track historical patterns for anomaly detection"""
    altar = models.ForeignKey(OrganizationUnit, on_delete=models.CASCADE)
    date = models.DateField()
    member_attendance = models.IntegerField(default=0)
    guest_count = models.IntegerField(default=0)
    total_attendance = models.IntegerField(default=0)
    avg_last_4_weeks = models.FloatField(null=True, blank=True)
    avg_last_12_weeks = models.FloatField(null=True, blank=True)
    guest_ratio = models.FloatField(null=True, blank=True)
    is_anomaly = models.BooleanField(default=False)
    anomaly_reason = models.TextField(null=True, blank=True)
    reviewed_by_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'altar_statistics'
        unique_together = ['altar', 'date']
        indexes = [
            models.Index(fields=['altar', 'date']),
            models.Index(fields=['is_anomaly', 'reviewed_by_admin']),
        ]


# ============================================
# SERVICE SCHEDULES
# ============================================

class ServiceSchedule(models.Model):
    """Define when attendance can be recorded (time windows)"""
    organization_unit = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.CASCADE,
        related_name='service_schedules'
    )
    day_of_week = models.IntegerField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
        ]
    )
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_schedules'
        indexes = [
            models.Index(fields=['organization_unit', 'day_of_week']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.organization_unit.name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
