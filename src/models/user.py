from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    email: str = Field(sa_column_kwargs={"unique": True})
    email_verified: Optional[datetime] = None
    image: Optional[str] = None
    can_share_social_media: bool = Field(default=False)
    is_system_admin: bool = Field(default=False)