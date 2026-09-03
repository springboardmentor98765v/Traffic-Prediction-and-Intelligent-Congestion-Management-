from fastapi import Depends

from app.auth.router import get_current_user
from app.core.exceptions import forbidden_error
from app.database.models import User


def require_role(*allowed_roles):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ):
        role_name = current_user.role.name if current_user.role else None

        if role_name not in allowed_roles:
            raise forbidden_error()

        return current_user

    return role_checker
