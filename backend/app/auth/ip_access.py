from fastapi import HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import BlockedIPAddress, User, UserIPAddress


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    if request.client:
        return request.client.host

    return "unknown"


def ensure_ip_allowed(db: Session, ip_address: str) -> None:
    blocked = db.scalar(select(BlockedIPAddress).where(BlockedIPAddress.ip_address == ip_address))
    if blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your IP address has been blocked")


def record_user_ip(db: Session, user: User, ip_address: str) -> None:
    if not ip_address or ip_address == "unknown":
        return

    user_ip = db.scalar(
        select(UserIPAddress).where(
            UserIPAddress.user_id == user.id,
            UserIPAddress.ip_address == ip_address,
        )
    )
    if user_ip:
        user_ip.request_count += 1
        user_ip.last_seen_at = func.now()
    else:
        user_ip = UserIPAddress(user_id=user.id, ip_address=ip_address)
        db.add(user_ip)

    db.commit()
