from rest_framework import permissions


class IsAdminOrReadOnlyForProject(permissions.BasePermission):
    """
    Project-level rule:
    - Anyone authenticated can list/retrieve projects they belong to.
    - Only Admins can create/update/delete projects.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.role == "ADMIN")


class IsAdminOrAssignedMember(permissions.BasePermission):
    """
    Task-level object permission (this is the RBAC centerpiece of the project):
    - Admins can view/edit any task.
    - Members can only view/edit tasks assigned to them.

    `has_permission` runs first, before Django even fetches the object -
    it's a coarse "are you allowed to hit this endpoint at all" check.
    `has_object_permission` runs afterwards, once DRF has the specific
    object, and is where the *per-row* ownership check happens.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMIN":
            return True
        return obj.assignee_id == request.user.id
