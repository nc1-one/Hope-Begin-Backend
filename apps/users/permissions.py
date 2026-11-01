from rest_framework import permissions

# Everyone who signs in to the admin panel. 'admin' is the super admin;
# 'staff' admins see everything except the financials and the admin team.
ADMIN_ROLES = ('admin', 'staff')


def is_superadmin(user):
    return bool(
        user and user.is_authenticated and user.is_staff
        and getattr(user, 'role', None) == 'admin'
    )


def is_admin_team(user):
    return bool(
        user and user.is_authenticated and user.is_staff
        and getattr(user, 'role', None) in ADMIN_ROLES
    )


def is_approved_carrier(user):
    return bool(
        user and user.is_authenticated and user.is_active
        and getattr(user, 'role', None) == 'carrier' and user.is_approved
    )


class IsAdminTeam(permissions.BasePermission):
    """Everyone who signs in to the admin panel, super admin or staff."""
    def has_permission(self, request, view):
        return is_admin_team(request.user)


class IsAdminTeamOrCarrier(permissions.BasePermission):
    """The admin team, or a Hope Carrier the team has approved."""
    def has_permission(self, request, view):
        return is_admin_team(request.user) or is_approved_carrier(request.user)


class IsSuperAdmin(permissions.BasePermission):
    """
    Super admins only: the financials and adding or removing admins.
    """
    def has_permission(self, request, view):
        return is_superadmin(request.user)


class CanManageUser(permissions.BasePermission):
    """
    Super admins manage anyone. Staff admins manage Hope Carriers and members,
    never other admins.
    """
    def has_object_permission(self, request, view, obj):
        if is_superadmin(request.user):
            return True
        return is_admin_team(request.user) and obj.role not in ADMIN_ROLES


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if obj == request.user:
            return True
        return CanManageUser().has_object_permission(request, view, obj)

class IsApproved(permissions.BasePermission):
    """
    Custom permission to only allow approved users to access the API.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_approved)
