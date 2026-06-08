from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session, selectinload

from app.auth.deps import get_current_admin
from app.auth.ip_access import get_client_ip
from app.config import settings
from app.database import get_db
from app.models.user import BlockedIPAddress, User, UserIPAddress
from app.schemas.admin import AdminIPRead, AdminStatsRead, AdminUserRead, IPBlockRequest

router = APIRouter(prefix="/admin", tags=["admin"])


def _blocked_map(db: Session) -> dict[str, BlockedIPAddress]:
    blocked = db.scalars(select(BlockedIPAddress)).all()
    return {item.ip_address: item for item in blocked}


def _ip_read(user_ip: UserIPAddress, blocked: dict[str, BlockedIPAddress], user: User | None = None) -> AdminIPRead:
    block = blocked.get(user_ip.ip_address)
    owner = user or user_ip.user
    return AdminIPRead(
        ip_address=user_ip.ip_address,
        user_id=user_ip.user_id,
        username=owner.username,
        email=owner.email,
        request_count=user_ip.request_count,
        first_seen_at=user_ip.first_seen_at,
        last_seen_at=user_ip.last_seen_at,
        is_blocked=block is not None,
        block_reason=block.reason if block else None,
    )


def _sorted_user_ips(user: User) -> list[UserIPAddress]:
    return sorted(user.ip_addresses, key=lambda item: item.last_seen_at, reverse=True)


@router.get("/stats", response_model=AdminStatsRead)
def admin_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> AdminStatsRead:
    active_since = datetime.now(UTC) - timedelta(minutes=settings.active_window_minutes)
    active_users = db.scalar(
        select(func.count(distinct(UserIPAddress.user_id))).where(UserIPAddress.last_seen_at >= active_since)
    ) or 0
    active_ips = db.scalar(
        select(func.count(distinct(UserIPAddress.ip_address))).where(UserIPAddress.last_seen_at >= active_since)
    ) or 0
    total_users = db.scalar(select(func.count(User.id))) or 0
    locked_users = db.scalar(select(func.count(User.id)).where(User.is_locked.is_(True))) or 0
    blocked_ips = db.scalar(select(func.count(BlockedIPAddress.id))) or 0
    return AdminStatsRead(
        active_users=active_users,
        active_ips=active_ips,
        total_users=total_users,
        locked_users=locked_users,
        blocked_ips=blocked_ips,
        window_minutes=settings.active_window_minutes,
    )


@router.get("/users", response_model=list[AdminUserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[AdminUserRead]:
    users = db.scalars(
        select(User)
        .options(selectinload(User.ip_addresses))
        .order_by(User.created_at.desc(), User.id.desc())
    ).all()
    blocked = _blocked_map(db)
    return [
        AdminUserRead(
            id=user.id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin,
            is_locked=user.is_locked,
            locked_at=user.locked_at,
            created_at=user.created_at,
            ip_addresses=[_ip_read(user_ip, blocked, user) for user_ip in _sorted_user_ips(user)],
        )
        for user in users
    ]


@router.post("/users/{user_id}/lock", response_model=AdminUserRead)
def lock_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> AdminUserRead:
    if user_id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot lock your own admin account")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_locked = True
    user.locked_at = func.now()
    db.commit()
    db.refresh(user)
    blocked = _blocked_map(db)
    return AdminUserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        is_locked=user.is_locked,
        locked_at=user.locked_at,
        created_at=user.created_at,
        ip_addresses=[_ip_read(user_ip, blocked, user) for user_ip in _sorted_user_ips(user)],
    )


@router.post("/users/{user_id}/unlock", response_model=AdminUserRead)
def unlock_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> AdminUserRead:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_locked = False
    user.locked_at = None
    db.commit()
    db.refresh(user)
    blocked = _blocked_map(db)
    return AdminUserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        is_locked=user.is_locked,
        locked_at=user.locked_at,
        created_at=user.created_at,
        ip_addresses=[_ip_read(user_ip, blocked, user) for user_ip in _sorted_user_ips(user)],
    )


@router.get("/ip-addresses", response_model=list[AdminIPRead])
def list_ip_addresses(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[AdminIPRead]:
    blocked = _blocked_map(db)
    seen_ips = db.scalars(
        select(UserIPAddress)
        .options(selectinload(UserIPAddress.user))
        .order_by(UserIPAddress.last_seen_at.desc(), UserIPAddress.id.desc())
    ).all()
    rows = [_ip_read(user_ip, blocked) for user_ip in seen_ips]
    seen_values = {row.ip_address for row in rows}

    for ip_address, block in blocked.items():
        if ip_address not in seen_values:
            rows.append(
                AdminIPRead(
                    ip_address=ip_address,
                    is_blocked=True,
                    block_reason=block.reason,
                    first_seen_at=block.created_at,
                    last_seen_at=block.created_at,
                )
            )
    return rows


@router.post("/ip-blocks", response_model=AdminIPRead)
def block_ip_address(
    payload: IPBlockRequest,
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> AdminIPRead:
    ip_address = payload.ip_address.strip()
    if ip_address == get_client_ip(request):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot block your current IP")

    block = db.scalar(select(BlockedIPAddress).where(BlockedIPAddress.ip_address == ip_address))
    if block:
        block.reason = payload.reason
    else:
        block = BlockedIPAddress(ip_address=ip_address, reason=payload.reason)
        db.add(block)
    db.commit()
    db.refresh(block)
    return AdminIPRead(
        ip_address=block.ip_address,
        is_blocked=True,
        block_reason=block.reason,
        first_seen_at=block.created_at,
        last_seen_at=block.created_at,
    )


@router.delete("/ip-blocks/{ip_address}", status_code=status.HTTP_204_NO_CONTENT)
def unblock_ip_address(
    ip_address: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> Response:
    block = db.scalar(select(BlockedIPAddress).where(BlockedIPAddress.ip_address == ip_address))
    if block:
        db.delete(block)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
