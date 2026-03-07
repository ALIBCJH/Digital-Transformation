from django.contrib import admin

# Removed unused imports
from django.utils.html import format_html

from .models import (
    Altar,
    AttendanceLog,
    Guest,
    Member,
    MemberTransferHistory,
    OrganizationNode,
    User,
)

# ============================================
# SUPER ADMIN ACCESS CONTROL
# ============================================

# Hardcoded list of 3 Super Admin emails
ALLOWED_SUPERADMIN_EMAILS = [
    "superadmin1@example.com",  # Replace with actual email
    "superadmin2@example.com",  # Replace with actual email
    "superadmin3@example.com",  # Replace with actual email
]


class SuperAdminAccessMixin:
    """
    Mixin to restrict Django Admin access to only the 3 authorized super admins.
    Applied to all ModelAdmin classes.
    """

    def has_module_permission(self, request):
        """Control whether user can see the module in admin index"""
        if not request.user.is_authenticated:
            return False

        # Allow access only to hardcoded super admins
        if request.user.email in ALLOWED_SUPERADMIN_EMAILS:
            return True

        # Block everyone else
        return False

    def has_view_permission(self, request, obj=None):
        """Control whether user can view records"""
        if request.user.email in ALLOWED_SUPERADMIN_EMAILS:
            return True
        return False

    def has_add_permission(self, request):
        """Control whether user can add records"""
        if request.user.email in ALLOWED_SUPERADMIN_EMAILS:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        """Control whether user can edit records"""
        if request.user.email in ALLOWED_SUPERADMIN_EMAILS:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        """Control whether user can delete records"""
        if request.user.email in ALLOWED_SUPERADMIN_EMAILS:
            return True
        return False


# ============================================
# ORGANIZATION NODE ADMIN
# ============================================


@admin.register(OrganizationNode)
class OrganizationNodeAdmin(SuperAdminAccessMixin, admin.ModelAdmin):
    """
    Manage the organizational hierarchy (Continents → Countries → Regions → Sub-Regions)
    """

    list_display = [
        "name",
        "code",
        "depth_indicator",
        "parent",
        "current_leader",
        "total_altars",
        "total_members",
        "is_active",
    ]
    list_filter = ["depth", "is_active", "parent"]
    search_fields = ["name", "code", "path"]
    raw_id_fields = ["parent", "current_leader"]
    readonly_fields = ["path", "depth", "hierarchy_view"]

    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "code", "parent", "is_active")
        }),
        ("Leadership", {
            "fields": ("current_leader",)
        }),
        ("Hierarchy Metadata (Auto-generated)", {
            "fields": ("path", "depth", "hierarchy_view"),
            "classes": ("collapse",)
        }),
        ("Statistics (Cached)", {
            "fields": ("total_altars", "total_members"),
            "classes": ("collapse",)
        }),
    )

    def depth_indicator(self, obj):
        """Visual indicator of tree depth"""
        indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * obj.depth
        return format_html(f"{indent}↳ Depth {obj.depth}")

    depth_indicator.short_description = "Hierarchy Level"

    def hierarchy_view(self, obj):
        """Show the full path in a readable format"""
        if not obj.path:
            return "Root"
        parts = obj.path.strip("/").split("/")
        return " → ".join(parts)

    hierarchy_view.short_description = "Full Organizational Path"


# ============================================
# ALTAR ADMIN WITH REGIONAL FILTERING
# ============================================


@admin.register(Altar)
class AltarAdmin(SuperAdminAccessMixin, admin.ModelAdmin):
    """
    Manage physical worship locations with regional categorization.
    Super Admins can filter by region to see altars nationwide.
    """

    list_display = [
        "name",
        "code",
        "region_display",
        "city",
        "pastor",
        "member_count",
        "status_badge",
    ]

    # CRITICAL: Regional filtering for master view
    list_filter = [
        "is_active",
        "parent_node",  # Filter by organizational node (Region/Sub-Region)
        "city",
    ]

    # CRITICAL: Global search across all altars
    search_fields = ["name", "code", "city", "parent_node__name", "parent_node__path"]

    raw_id_fields = ["parent_node", "pastor"]
    readonly_fields = ["organizational_path_display", "member_count", "created_at", "updated_at"]

    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "code", "parent_node", "is_active")
        }),
        ("Location", {
            "fields": ("address", "city", "latitude", "longitude")
        }),
        ("Leadership", {
            "fields": ("pastor",)
        }),
        ("Statistics", {
            "fields": ("member_count", "capacity", "established_date"),
            "classes": ("collapse",)
        }),
        ("Metadata", {
            "fields": ("organizational_path_display", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def region_display(self, obj):
        """Show the region/sub-region this altar belongs to"""
        if obj.parent_node:
            return obj.parent_node.name
        return format_html('<span style="color: gray;">Standalone</span>')

    region_display.short_description = "Region/Sub-Region"
    region_display.admin_order_field = "parent_node__name"

    def status_badge(self, obj):
        """Visual status indicator"""
        if obj.is_active:
            return format_html('<span style="color: green;">● Active</span>')
        return format_html('<span style="color: red;">○ Inactive</span>')

    status_badge.short_description = "Status"

    def organizational_path_display(self, obj):
        """Show full organizational path"""
        if obj.parent_node:
            return obj.parent_node.path + obj.code + "/"
        return f"/{obj.code}/ (Root level)"

    organizational_path_display.short_description = "Organizational Path"


# ============================================
# USER ADMIN
# ============================================


@admin.register(User)
class UserAdmin(SuperAdminAccessMixin, admin.ModelAdmin):
    """
    Manage users (both regular members and admins).
    Shows organizational scope for administrators.
    """

    list_display = [
        "username",
        "email",
        "full_name_display",
        "home_altar",
        "admin_scope",
        "role_badge",
        "status",
    ]

    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "phone_verified",
        "home_altar__parent_node",  # Regional filter
    ]

    search_fields = [
        "username",
        "email",
        "phone_number",
        "first_name",
        "last_name",
        "home_altar__name",
        "admin_scope__name",
    ]

    raw_id_fields = ["home_altar", "admin_scope"]
    readonly_fields = ["created_at", "updated_at", "last_login", "date_joined"]

    fieldsets = (
        ("Authentication", {
            "fields": ("username", "email", "password")
        }),
        ("Personal Information", {
            "fields": ("first_name", "last_name", "phone_number", "phone_verified")
        }),
        ("Organizational Affiliation", {
            "fields": ("home_altar", "admin_scope")
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "classes": ("collapse",)
        }),
        ("Important Dates", {
            "fields": ("last_login", "date_joined", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def full_name_display(self, obj):
        """Show full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or "—"

    full_name_display.short_description = "Full Name"

    def role_badge(self, obj):
        """Visual role indicator"""
        if obj.is_superuser:
            return format_html('<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px;">SUPER ADMIN</span>')
        elif obj.is_staff:
            return format_html('<span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px;">STAFF</span>')
        elif obj.admin_scope:
            return format_html('<span style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px;">REGIONAL ADMIN</span>')
        return format_html('<span style="background: #6c757d; color: white; padding: 2px 6px; border-radius: 3px;">USER</span>')

    role_badge.short_description = "Role"

    def status(self, obj):
        """Active/Inactive status"""
        if obj.is_active:
            return format_html('<span style="color: green;">● Active</span>')
        return format_html('<span style="color: red;">○ Inactive</span>')

    status.short_description = "Status"


# ============================================
# MEMBER ADMIN - THE GLOBAL MASTER VIEW
# ============================================


@admin.register(Member)
class MemberAdmin(SuperAdminAccessMixin, admin.ModelAdmin):
    """
    THE GLOBAL PIPE - Master view of all members nationwide.
    Super Admins can filter by region, altar, and search across the entire nation.
    """

    list_display = [
        "full_name",
        "phone_number",
        "gender_icon",
        "home_altar",
        "region_display",
        "membership_date",
        "status_badge",
    ]

    # CRITICAL: Regional categorization for master view
    list_filter = [
        "is_active",
        "home_altar__parent_node",  # Filter by Region/Sub-Region
        "home_altar",  # Filter by specific Altar
        "gender",
        "membership_date",
    ]

    # CRITICAL: Global search - find any member in the country
    search_fields = [
        "full_name",
        "phone_number",
        "email",
        "home_altar__name",
        "home_altar__parent_node__name",
        "home_altar__parent_node__path",
    ]

    raw_id_fields = ["home_altar"]
    readonly_fields = ["created_at", "updated_at", "attendance_summary"]
    date_hierarchy = "membership_date"

    fieldsets = (
        ("Personal Information", {
            "fields": ("full_name", "phone_number", "email", "gender", "date_of_birth")
        }),
        ("Church Affiliation", {
            "fields": ("home_altar", "membership_date", "is_active")
        }),
        ("Statistics & History", {
            "fields": ("attendance_summary",),
            "classes": ("collapse",)
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def region_display(self, obj):
        """Show which region this member belongs to"""
        if obj.home_altar and obj.home_altar.parent_node:
            # Get the ancestors to find the region
            ancestors = obj.home_altar.parent_node.get_ancestors()
            if ancestors.exists():
                # Typically, the first or second level is the Region
                region = ancestors.filter(depth__lte=2).last()
                if region:
                    return region.name
            return obj.home_altar.parent_node.name
        return format_html('<span style="color: gray;">—</span>')

    region_display.short_description = "Region"
    region_display.admin_order_field = "home_altar__parent_node__name"

    def gender_icon(self, obj):
        """Visual gender indicator"""
        if obj.gender.upper() == "M":
            return format_html('<span title="Male">👨</span>')
        elif obj.gender.upper() == "F":
            return format_html('<span title="Female">👩</span>')
        return "—"

    gender_icon.short_description = "Gender"

    def status_badge(self, obj):
        """Active/Inactive visual indicator"""
        if obj.is_active:
            return format_html('<span style="color: green;">● Active</span>')
        return format_html('<span style="color: red;">○ Inactive</span>')

    status_badge.short_description = "Status"

    def attendance_summary(self, obj):
        """Show attendance statistics for this member"""
        total_attendance = AttendanceLog.objects.filter(member=obj).count()
        if total_attendance == 0:
            return "No attendance records"

        recent_attendance = AttendanceLog.objects.filter(
            member=obj
        ).order_by("-service_date")[:5]

        # Build list items safely
        list_items = "".join([
            format_html("<li>{} - {}</li>", log.service_date, log.get_service_type_display())
            for log in recent_attendance
        ])

        return format_html(
            "<strong>Total Services Attended:</strong> {}<br><br>"
            "<strong>Recent Attendance:</strong><ul>{}</ul>",
            total_attendance,
            list_items
        )

    attendance_summary.short_description = "Attendance Summary"


# ============================================
# ATTENDANCE LOG ADMIN
# ============================================


@admin.register(AttendanceLog)
class AttendanceLogAdmin(SuperAdminAccessMixin, admin.ModelAdmin):
    """
    Track attendance records across all altars.
    Super Admins can analyze attendance by region, service type, etc.
    """

    list_display = [
        "member_display",
        "altar_display",
        "service_date",
        "service_type",
        "timestamp",
    ]

    list_filter = [
        "service_type",
        "service_date",
        "altar__parent_node",  # Regional filter
        "altar",
    ]

    search_fields = [
        "member__full_name",
        "guest__full_name",
        "altar__name",
        "altar__parent_node__name",
    ]

    raw_id_fields = ["member", "guest", "altar"]
    date_hierarchy = "service_date"
    readonly_fields = ["timestamp"]

    def member_display(self, obj):
        """Show who attended"""
        if obj.member:
            return obj.member.full_name
        elif obj.guest:
            return format_html('<span style="color: #6c757d;">{} (Guest)</span>', obj.guest.full_name)
        return "—"

    member_display.short_description = "Attendee"

    def altar_display(self, obj):
        """Show which altar"""
        if obj.altar:
            return obj.altar.name
        return "—"

    altar_display.short_description = "Altar"


# ============================================
# GUEST & TRANSFER HISTORY ADMIN
# ============================================


@admin.register(Guest)
class GuestAdmin(SuperAdminAccessMixin, admin.ModelAdmin):
    """Track visitors and guests"""

    list_display = ["full_name", "phone_number", "visited_altar", "visit_count", "last_visit_date"]
    list_filter = ["visited_altar__parent_node", "visited_altar", "first_visit_date"]
    search_fields = ["full_name", "phone_number", "visited_altar__name", "visiting_from"]
    raw_id_fields = ["visited_altar"]
    date_hierarchy = "last_visit_date"


@admin.register(MemberTransferHistory)
class MemberTransferHistoryAdmin(SuperAdminAccessMixin, admin.ModelAdmin):
    """Track member transfers between altars"""

    list_display = ["member", "from_altar", "to_altar", "transfer_reason", "transfer_date", "processed_by"]
    list_filter = [
        "transfer_reason",
        "transfer_date",
        "from_altar__parent_node",
        "to_altar__parent_node",
    ]
    search_fields = ["member__full_name", "from_altar__name", "to_altar__name", "notes"]
    raw_id_fields = ["member", "from_altar", "to_altar", "processed_by"]
    date_hierarchy = "transfer_date"
    readonly_fields = ["created_at"]


# ============================================
# ADMIN SITE CUSTOMIZATION
# ============================================

admin.site.site_header = "Digital Transformation Super Admin"
admin.site.site_title = "DT Admin Portal"
admin.site.index_title = "Master Control Panel - Nationwide View"
