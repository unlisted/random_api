from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text, func
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as postgresql_UUID



class Base(DeclarativeBase):
    pass

class RenderedModel(Base):
    __tablename__ = "rendered_model"

    id: Mapped[int] = mapped_column(postgresql_UUID, primary_key=True, server_default=func.gen_random_uuid())
    uid: Mapped[UUID] = mapped_column()
    body: Mapped[str] = mapped_column(Text)



