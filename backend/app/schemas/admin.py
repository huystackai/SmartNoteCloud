from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class AdminIPRead(BaseModel):
    ip_address: str
    user_id: int | None = None
    username: str | None = None
    email: EmailStr | None = None
    request_count: int = 0
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    is_blocked: bool = False
    block_reason: str | None = None


class AdminUserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool
    is_locked: bool
    created_at: datetime
    locked_at: datetime | None = None
    ip_addresses: list[AdminIPRead] = []


class IPBlockRequest(BaseModel):
    ip_address: str = Field(min_length=3, max_length=64)
    reason: str | None = Field(default=None, max_length=255)


class AdminStatsRead(BaseModel):
    active_users: int
    active_ips: int
    total_users: int
    locked_users: int
    blocked_ips: int
    window_minutes: int
