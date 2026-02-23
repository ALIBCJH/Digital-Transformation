from django.contrib import admin

from .models import Altar, Member, OrganizationNode, User


@admin.register(OrganizationNode)
class OrganizationNodeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "depth",
        "parent",
        "current_leader",
        "is_active",
        "total_altars",
        "total_members",
    ]
    list_filter = ["depth", "is_active"]
    search_fields = ["name", "code", "path"]
    raw_id_fields = ["parent", "current_leader"]
    readonly_fields = ["path", "depth"]


@admin.register(Altar)
class AltarAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "parent_node",
        "city",
        "pastor",
        "member_count",
        "is_active",
    ]
    list_filter = ["is_active", "city"]
    search_fields = ["name", "code", "city"]
    raw_id_fields = ["parent_node", "pastor"]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "phone_number",
        "home_altar",
        "admin_scope",
        "is_active",
    ]
    list_filter = ["is_active", "phone_verified", "is_staff", "is_superuser"]
    search_fields = ["username", "email", "phone_number", "first_name", "last_name"]
    raw_id_fields = ["home_altar", "admin_scope"]


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone_number", "gender", "home_altar", "is_active"]
    list_filter = ["gender", "is_active"]
    search_fields = ["full_name", "phone_number", "email"]
    raw_id_fields = ["home_altar"]
    readonly_fields = ["created_at"]
