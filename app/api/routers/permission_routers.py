from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import admin_required, get_db
from app.schemas.permission import PermissionCreate, PermissionResponse
from app.services.permission_service import PermissionManagementService

router = APIRouter(
    prefix="/permission", tags=["Permission"], dependencies=[Depends(admin_required)]
)


@router.get("/id/{permission_id}", response_model=PermissionResponse)
async def get_permission_by_id(
    permission_id: int, db: AsyncSession = Depends(get_db)
) -> PermissionResponse:

    service = PermissionManagementService(db)
    permission = await service.get_by_id(permission_id)
    return permission


@router.get("/code/{code}", response_model=PermissionResponse)
async def get_permission_by_code(
    code: str, db: AsyncSession = Depends(get_db)
) -> PermissionResponse:

    service = PermissionManagementService(db)
    permission = await service.get_by_code(code)
    return permission


@router.get("/", response_model=List[PermissionResponse])
async def get_all_permissions(
    db: AsyncSession = Depends(get_db),
) -> List[PermissionResponse]:

    service = PermissionManagementService(db)
    permissions = await service.get_all_permissions()
    return permissions


@router.post("/", response_model=PermissionResponse, status_code=201)
async def create_permission(
    permission_data: PermissionCreate, db: AsyncSession = Depends(get_db)
) -> PermissionResponse:

    service = PermissionManagementService(db)
    permission = await service.create_permission(permission_data)
    return permission


@router.patch("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
) -> PermissionResponse:

    service = PermissionManagementService(db)
    permission = await service.update_permission(permission_id, permission_data)
    return permission


@router.delete("/{permission_id}", status_code=204)
async def delete_permission(permission_id: int, db: AsyncSession = Depends(get_db)):

    service = PermissionManagementService(db)
    await service.delete_permission(permission_id)
    return None
