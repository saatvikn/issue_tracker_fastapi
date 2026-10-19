from uuid import uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

from sqlalchemy import Enum as SQLAlchemyEnum

from app.enums import IssuePriority, IssueStatus

from datetime import datetime

from sqlalchemy import DateTime, func


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    title: Mapped[str] = mapped_column(String(100))

    description: Mapped[str] = mapped_column(String(1000))

    priority: Mapped[IssuePriority] = mapped_column(
        SQLAlchemyEnum(IssuePriority, name="issue_priority"),
        default=IssuePriority.medium,
    )

    status: Mapped[IssueStatus] = mapped_column(
        SQLAlchemyEnum(IssueStatus, name="issue_status"),
        default=IssueStatus.open,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
