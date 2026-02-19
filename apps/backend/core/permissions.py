from rest_framework import permissions
from core.models import OrganizationNode, Altar


class HasOrganizationalScope(permissions.BasePermission):
    """
    Permission to check if admin has organizational scope assigned.
    Superusers bypass this check.
    """
    message = "You must be assigned to an organizational unit (region, sub-region, or altar) to perform this action."

    def has_permission(self, request, view):
        # Superusers can do anything
        if request.user.is_superuser:
            return True

        # User must be authenticated and have admin_scope assigned
        return (
            request.user.is_authenticated and
            request.user.admin_scope is not None
        )


class CanManageMembers(permissions.BasePermission):
    """
    Permission to check if admin can manage members based on their organizational scope.
    Admins can only manage members within their assigned organizational unit and its descendants.
    """
    message = "You can only manage members within your organizational scope."

    def has_permission(self, request, view):
        # Superusers can do anything
        if request.user.is_superuser:
            return True

        # User must have organizational scope
        if not request.user.admin_scope:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # Superusers can do anything
        if request.user.is_superuser:
            return True

        # Check if the member's altar is within admin's scope
        if hasattr(obj, 'home_altar') and obj.home_altar:
            return request.user.can_manage_altar(obj.home_altar)

        return False


# TODO: Re-enable after creating Guest model
# class CanManageGuests(permissions.BasePermission):
#     """Permission to check if admin can manage guests based on their organizational scope."""
#     ...


# TODO: Re-enable after creating AttendanceLog model
# class CanRecordAttendance(permissions.BasePermission):
#     """Permission to check if admin can record attendance for a specific altar."""
#     ...


# TODO: Re-enable after creating MemberTransferHistory model
# class CanTransferMembers(permissions.BasePermission):
#     """Permission to check if admin can transfer members."""
#     ...
