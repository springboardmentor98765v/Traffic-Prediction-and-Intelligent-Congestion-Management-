from fastapi import HTTPException, status


def unauthorized_error():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )


def forbidden_error():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource",
    )


def not_found_error(resource: str):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found",
    )


def conflict_error(message: str):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )
