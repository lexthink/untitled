from functools import wraps

from ninja.errors import HttpError

from .enums import Role  # noqa: TC001


def require_roles(*roles: Role):
    """
    Decorator for API views that restricts access based on membership role.

    Usage:
        @router.post("/")
        @require_roles(Role.OWNER, Role.ADMIN)
        def create_location(request, data: LocationInputSchema):
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            membership = getattr(request, "membership", None)
            if not membership:
                raise HttpError(403, "Organization context required.")
            if membership.role not in roles:
                raise HttpError(
                    403,
                    "You don't have permission to perform this action.",
                )
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
