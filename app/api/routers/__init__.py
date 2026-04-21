from .auth_routers import router as auth_router
from .permission_routers import router as permission_router
from .role_routers import router as role_router
from .user_routers import router as user_router

__all__ = ["auth_router", "user_router", "role_router", "permission_router"]
