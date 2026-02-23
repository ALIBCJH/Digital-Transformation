"""
REDESIGNED MODELS FOR SCALABLE HIERARCHICAL ORGANIZATION
=========================================================

This redesign implements:
1. Recursive self-referential OrganizationNode (
   eliminates separate Region/Sub-Region tables
)
2. Optimized tree traversal with Postgres indexing
3. Multi-tenant filtering at the database level
4. Separate Altar entity for physical locations
5. Materialized Path pattern for O(1) ancestor queries
"""

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import Q

# ============================================
# CORE HIERARCHICAL ORGANIZATION
# ============================================

class OrganizationNode(models.Model):
    """
    Recursive tree structure for organization hierarchy.
    Uses Materialized Path pattern for efficient queries.

    Examples:
    - /GLOBAL/                           (Root)
    - /GLOBAL/AFRICA/                    (Continent)
    - /GLOBAL/AFRICA/KENYA/              (Country)
    - /GLOBAL/AFRICA/KENYA/CENTRAL/      (Region)
    - /GLOBAL/AFRICA/KENYA/CENTRAL/NYERI/ (Sub-Region)
    """

    # Core fields
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique identifier (e.g., CENTRAL, NYERI, ALTAR_001)"
    )

    # Self-referential parent relationship
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )

    # Materialized Path for O(1) ancestor queries
    path = models.CharField(
        max_length=1000,
        unique=True,
        db_index=True,
        help_text="Materialized path (e.g., /GLOBAL/AFRICA/KENYA/CENTRAL/)"
    )

    # Tree metadata
    depth = models.IntegerField(default=0, db_index=True)

    # Leadership
    current_leader = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leading_nodes'
    )

    # Metadata
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Statistics (cached counts)
    total_altars = models.IntegerField(default=0)
    total_members = models.IntegerField(default=0)

    class Meta:
        db_table = 'organization_nodes'
        indexes = [
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['depth', 'is_active']),
            models.Index(fields=['path']),  # Critical for ancestor queries
            # GIN index for path prefix matching (Postgres-specific)
            GinIndex(fields=['path'], name='path_gin_idx', opclasses=['gin_trgm_ops']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(depth__gte=0),
                name='depth_non_negative'
            )
        ]
        ordering = ['path']

    def __str__(self):
        return f"{self.name} (Depth {self.depth})"

    def save(self, *args, **kwargs):
        """Auto-generate path and depth on save"""
        if self.parent:
            self.path = f"{self.parent.path}{self.code}/"
            self.depth = self.parent.depth + 1
        else:
            # Root node
            self.path = f"/{self.code}/"
            self.depth = 0

        super().save(*args, **kwargs)

    def get_ancestors(self):
        """O(1) query for all ancestors using path prefix"""
        if not self.path:
            return OrganizationNode.objects.none()

        # Extract parent paths from materialized path
        # /GLOBAL/AFRICA/KENYA/ → [/GLOBAL/, /GLOBAL/AFRICA/]
        path_parts = self.path.strip('/').split('/')
        ancestor_paths = [
            '/' + '/'.join(path_parts[:i+1]) + '/'
            for i in range(len(path_parts) - 1)
        ]

        return OrganizationNode.objects.filter(
            path__in=ancestor_paths
        ).order_by('depth')

    def get_descendants(self, include_self=False):
        """O(1) query for all descendants using path prefix"""
        queryset = OrganizationNode.objects.filter(
            path__startswith=self.path,
            is_active=True
        )

        if not include_self:
            queryset = queryset.exclude(id=self.id)

        return queryset.order_by('depth', 'name')

    def get_children(self):
        """Direct children only (one level down)"""
        return self.children.filter(is_active=True).order_by('name')

    def get_siblings(self):
        """Nodes at the same level with same parent"""
        if not self.parent:
            return OrganizationNode.objects.none()

        return OrganizationNode.objects.filter(
            parent=self.parent,
            is_active=True
        ).exclude(id=self.id).order_by('name')

    def get_root(self):
        """O(1) query for root node"""
        if self.depth == 0:
            return self

        # First part of path is always root
        root_code = self.path.strip('/').split('/')[0]
        return OrganizationNode.objects.get(code=root_code)

    def is_ancestor_of(self, node):
        """Check if this node is an ancestor of another node"""
        return node.path.startswith(self.path) and node.id != self.id

    def is_descendant_of(self, node):
        """Check if this node is a descendant of another node"""
        return self.path.startswith(node.path) and self.id != node.id


class Altar(models.Model):
    """
    Physical worship locations (leaf nodes of the organization tree).
    Separated from OrganizationNode for clarity and specific altar operations.
    """

    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)

    # Link to parent node (typically a Sub-Region)
    parent_node = models.ForeignKey(
        OrganizationNode,
        on_delete=models.CASCADE,
        related_name='altars',
        db_index=True
    )

    # Location details
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    # Leadership
    pastor = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pastoring_altars'
    )

    # Metadata
    is_active = models.BooleanField(default=True, db_index=True)
    established_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Statistics
    member_count = models.IntegerField(default=0)
    capacity = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'altars'
        indexes = [
            models.Index(fields=['parent_node', 'is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['city']),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.parent_node.name})"

    def get_organizational_path(self):
        """Get full organizational path including altar"""
        return f"{self.parent_node.path}{self.code}/"


# ============================================
# USER MODEL WITH MULTI-TENANT SCOPE
# ============================================

class User(AbstractUser):
    """
    Extended user with organizational scope for multi-tenant filtering.
    """

    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Home altar (where user worships)
    home_altar = models.ForeignKey(
        Altar,
        on_delete=models.PROTECT,
        related_name='home_members',
        null=True,
        blank=True
    )

    # Administrative scope (for multi-tenant filtering)
    admin_scope = models.ForeignKey(
        OrganizationNode,
        on_delete=models.PROTECT,
        related_name='admins',
        null=True,
        blank=True,
        help_text=(
            'The organizational node this user can manage '
            '(e.g., Central Region, Nyeri Sub-Region)'
        )
    )

    # Metadata
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Django auth overrides
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='core_users',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='core_users',
    )

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['admin_scope', 'is_active']),
            models.Index(fields=['home_altar']),
        ]

    def get_accessible_nodes(self):
        """
        Multi-tenant filter: Get all nodes this user can access.
        Returns the admin scope and all its descendants.
        """
        if self.is_superuser:
            # Superusers see everything
            return OrganizationNode.objects.filter(is_active=True)

        if not self.admin_scope:
            # No scope = no access
            return OrganizationNode.objects.none()

        # Return scope + all descendants (O(1) query via path)
        return self.admin_scope.get_descendants(include_self=True)

    def get_accessible_altars(self):
        """Get all altars within user's scope"""
        if self.is_superuser:
            return Altar.objects.filter(is_active=True)

        if not self.admin_scope:
            return Altar.objects.none()

        # Get all altars under accessible nodes
        accessible_nodes = self.get_accessible_nodes()
        return Altar.objects.filter(
            parent_node__in=accessible_nodes,
            is_active=True
        )

    def can_manage_node(self, node):
        """Check if user can manage a specific node"""
        if self.is_superuser:
            return True

        if not self.admin_scope:
            return False

        # User can manage if node is within their scope
        return node.is_descendant_of(self.admin_scope) or node.id == self.admin_scope.id

    def can_manage_altar(self, altar):
        """Check if user can manage a specific altar"""
        return self.can_manage_node(altar.parent_node)


# ============================================
# HELPER MODELS
# ============================================

class Member(models.Model):
    """Church member profile"""
    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=255, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # Link to altar
    home_altar = models.ForeignKey(
        Altar,
        on_delete=models.PROTECT,
        related_name='members',
        db_index=True
    )

    # Demographics
    gender = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # Membership info
    membership_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'members'
        indexes = [
            models.Index(fields=['home_altar', 'is_active']),
            models.Index(fields=['full_name']),
        ]

    def __str__(self):
        return self.full_name


class MemberTransferHistory(models.Model):
    """
    Track member transfers between altars and offboarding.
    Records both internal transfers and departures.
    """

    TRANSFER_REASONS = [
        ('job_transfer', 'Job Transfer'),
        ('relocation', 'Relocation'),
        ('family_reasons', 'Family Reasons'),
        ('personal_choice', 'Personal Choice'),
        ('offboarding', 'Offboarding/Leaving'),
        ('other', 'Other'),
    ]

    id = models.BigAutoField(primary_key=True)

    # Member being transferred
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='transfer_history',
        db_index=True
    )

    # Transfer details
    from_altar = models.ForeignKey(
        Altar,
        on_delete=models.PROTECT,
        related_name='transfers_out',
        db_index=True
    )

    to_altar = models.ForeignKey(
        Altar,
        on_delete=models.PROTECT,
        related_name='transfers_in',
        null=True,
        blank=True,
        help_text='Null if member is being offboarded/deactivated'
    )

    # Reason and notes (matching existing DB schema)
    transfer_reason = models.CharField(
        max_length=50,
        choices=TRANSFER_REASONS,
        default='other',
        db_column='transfer_reason'
    )
    transfer_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    # Audit trail (matching existing DB schema)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='transfers_processed',
        db_column='processed_by_id',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'member_transfer_history'
        indexes = [
            models.Index(fields=['member', 'created_at']),
            models.Index(fields=['from_altar', 'created_at']),
            models.Index(fields=['to_altar', 'created_at']),
        ]
        ordering = ['-created_at']
        verbose_name_plural = 'Member transfer histories'

    def __str__(self):
        if self.to_altar:
            return (
                f"{self.member.full_name}: "
                f"{self.from_altar.name} → {self.to_altar.name}"
            )
        return f"{self.member.full_name}: Offboarded from {self.from_altar.name}"


class Guest(models.Model):
    """
    Visitor/guest tracking for altar visits.
    Tracks first-time visitors and repeat guests.
    """

    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=255, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, blank=True)

    # Which altar they visited (if exists in DB, otherwise NULL for old data)
    visited_altar = models.ForeignKey(
        Altar,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guests',
        db_column='visited_altar_id'
    )

    # Where they're from
    visiting_from = models.CharField(max_length=255, blank=True)

    # Visit tracking
    first_visit_date = models.DateField()
    last_visit_date = models.DateField()
    visit_count = models.IntegerField(default=1)

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'guests'
        indexes = [
            models.Index(fields=['visited_altar', 'last_visit_date']),
            models.Index(fields=['full_name']),
        ]
        ordering = ['-last_visit_date']

    def __str__(self):
        return f"{self.full_name} ({self.visit_count} visits)"


class AttendanceLog(models.Model):
    """
    Track member and guest attendance at services.
    Records who attended which service at which altar.
    """

    SERVICE_TYPES = [
        ('sunday_service', 'Sunday Service'),
        ('midweek_service', 'Midweek Service'),
        ('special_service', 'Special Service'),
        ('prayer_meeting', 'Prayer Meeting'),
        ('other', 'Other'),
    ]

    id = models.BigAutoField(primary_key=True)

    # Service details
    service_date = models.DateField(db_index=True)
    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_TYPES,
        default='sunday_service'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    # Who attended (either member or guest)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='attendance_logs',
        null=True,
        blank=True,
        db_column='member_id'
    )
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name='attendance_logs',
        null=True,
        blank=True,
        db_column='guest_id'
    )

    # Location (organizational hierarchy)
    altar = models.ForeignKey(
        Altar,
        on_delete=models.PROTECT,
        related_name='attendance_logs',
        db_column='altar_id'
    )
    sub_region = models.ForeignKey(
        OrganizationNode,
        on_delete=models.PROTECT,
        related_name='sub_region_attendance',
        null=True,
        blank=True,
        db_column='sub_region_id'
    )
    region = models.ForeignKey(
        OrganizationNode,
        on_delete=models.PROTECT,
        related_name='region_attendance',
        null=True,
        blank=True,
        db_column='region_id'
    )
    country = models.ForeignKey(
        OrganizationNode,
        on_delete=models.PROTECT,
        related_name='country_attendance',
        null=True,
        blank=True,
        db_column='country_id'
    )
    continent = models.ForeignKey(
        OrganizationNode,
        on_delete=models.PROTECT,
        related_name='continent_attendance',
        null=True,
        blank=True,
        db_column='continent_id'
    )

    # Who recorded this attendance
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='attendance_recorded',
        db_column='recorded_by_id'
    )

    class Meta:
        db_table = 'attendance_logs'
        indexes = [
            models.Index(fields=['service_date', 'altar']),
            models.Index(fields=['member', 'service_date']),
            models.Index(fields=['guest', 'service_date']),
        ]
        ordering = ['-service_date', '-timestamp']
        constraints = [
            models.CheckConstraint(
                check=Q(member__isnull=False) | Q(guest__isnull=False),
                name='attendance_must_have_member_or_guest'
            )
        ]

    def __str__(self):
        if self.member:
            return f"{self.member.full_name} - {self.service_date}"
        elif self.guest:
            return f"{self.guest.full_name} (Guest) - {self.service_date}"
        return f"Attendance #{self.id} - {self.service_date}"
