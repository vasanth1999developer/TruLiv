from rest_framework.permissions import BasePermission


class RoleBasedPermission(BasePermission):
    """
    Allows access only to users with a specific role.
    """

    allowed_roles = []

    def has_permission(self, request, view):
        """This is used to get the role from the request User"""
        # breakpoint()
        user_role = getattr(request.user, "role", None)
        allowed_roles = getattr(view, "allowed_roles", [])
        return user_role in allowed_roles
