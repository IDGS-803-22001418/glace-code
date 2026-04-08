from functools import wraps
from typing import Callable, ParamSpec, TypeVar, cast

from flask import abort
from flask_login import current_user  # type: ignore

P = ParamSpec("P")
R = TypeVar("R")


def roles_required(*roles: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    allowed_roles = {role.strip().lower() for role in roles if role and role.strip()}

    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @wraps(f)
        def decorated_function(*args: P.args, **kwargs: P.kwargs) -> R:
            user_role = getattr(current_user, "rol_asignado", "")
            if (
                not current_user.is_authenticated
                or str(user_role).strip().lower() not in allowed_roles
            ):
                abort(403)  # Forbidden
            return f(*args, **kwargs)

        return cast(Callable[P, R], decorated_function)

    return decorator
