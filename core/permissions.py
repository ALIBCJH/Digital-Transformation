from rest_framework import permissions
from core.models import OrganizationUnit


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
        
        # User must be authenticated and have organizational_unit assigned
        return (
            request.user.is_authenticated and
            request.user.organizational_unit is not None
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
        if not request.user.organizational_unit:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # Superusers can do anything
        if request.user.is_superuser:
            return True

        # Check if the member's altar is within admin's scope
        if hasattr(obj, 'home_altar'):
            return request.user.can_manage_unit(obj.home_altar)
        
        return False


class CanManageGuests(permissions.BasePermission):
    """
    Permission to check if admin can manage guests based on their organizational scope.
    """
    message = "You can only manage guests within your organizational scope."

    def has_permission(self, request, view):
        # Superusers can do anything
        if request.user.is_superuser:
            return True

        # User must have organizational scope
        return (
            request.user.is_authenticated and
            request.user.organizational_unit is not None
        )


class CanRecordAttendance(permissions.BasePermission):
    """
    Permission to check if admin can record attendance for a specific altar.
    """
    message = "You can only record attendance for altars within your organizational scope."

    def has_permission(self, request, view):
        # Superusers can do anything
        if request.user.is_superuser:
            return True

        # User must have organizational scope
        if not request.user.organizational_unit:
            return False

        # For POST requests, check the altar in the request data
        if request.method == 'POST':
            altar_name = request.data.get('altar')
            if not altar_name:
                return False

            try:
                altar = OrganizationUnit.objects.get(name=altar_name, level='ALTAR')
                return request.user.can_manage_unit(altar)
            except OrganizationUnit.DoesNotExist:
                return False

        return True


class CanTransferMembers(permissions.BasePermission):
    """
    Permission to check if admin can transfer members.
    Admin must be able to manage both source and destination altars.
    """
    message = "You can only transfer members between altars within your organizational scope."

    def has_permission(self, request, view):
        # Superusers can do anything
        if request.user.is_superuser:
            return True

        # User must have organizational scope
        if not request.user.organizational_unit:
            return False

        # For POST requests, validate both source and destination
        if request.method == 'POST':
            member_id = request.data.get('member_id')
            to_altar_name = request.data.get('to_altar')

            if not member_id:
                return False

            try:
                from core.models import Member
                member = Member.objects.get(id=member_id)

                # Check if admin can manage source altar
                if not request.user.can_manage_unit(member.home_altar):
                    return False

                # If transferring (not deactivating), check destination altar
                if to_altar_name:
                    try:
                        to_altar = OrganizationUnit.objects.get(name=to_altar_name, level='ALTAR')
                        return request.user.can_manage_unit(to_altar)
                    except OrganizationUnit.DoesNotExist:
                        return False

                # Deactivating (no destination) is allowed if source is manageable
                return True

            except Member.DoesNotExist:
                return False

        return True
