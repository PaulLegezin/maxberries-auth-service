from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routers import auth_router, permission_router, role_router, user_router
from app.core.db import check_connection
from app.core.logger_config import logger
from app.models.permissions import Permission  # noqa: F401
from app.models.roles import Role, RolePermission  # noqa: F401
from app.models.users import User  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения...")

    await check_connection()

    yield
    logger.info("Остановка приложения...")


app = FastAPI(lifespan=lifespan, title="Maxberries Auth Service")


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(permission_router)


Instrumentator().instrument(app).expose(app)


@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}
