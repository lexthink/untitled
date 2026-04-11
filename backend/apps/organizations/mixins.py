from .enums import Role  # noqa: TC001


class OrganizationAdminMixin:
    """
    Mixin for ModelAdmin classes that belong to organization schemas.
    Controls visibility and permissions based on the user's membership role.

    Define roles per action on each ModelAdmin using the Role enum:
        view_roles = (Role.OWNER, Role.ADMIN, Role.MEMBER)
        add_roles = (Role.OWNER, Role.ADMIN)
        change_roles = (Role.OWNER,)
        delete_roles = (Role.OWNER,)

    If a role list is empty or not defined, only superusers have access.
    """

    view_roles: tuple[Role, ...] = ()
    add_roles: tuple[Role, ...] = ()
    change_roles: tuple[Role, ...] = ()
    delete_roles: tuple[Role, ...] = ()

    def _has_role(self, request, roles):
        if request.user.is_superuser:
            return True
        if not roles:
            return False
        membership = getattr(request, "membership", None)
        return membership is not None and membership.role in roles

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return self._has_role(request, self.view_roles)

    def has_view_permission(self, request, obj=None):
        return self._has_role(request, self.view_roles)

    def has_add_permission(self, request):
        return self._has_role(request, self.add_roles)

    def has_change_permission(self, request, obj=None):
        return self._has_role(request, self.change_roles)

    def has_delete_permission(self, request, obj=None):
        return self._has_role(request, self.delete_roles)
