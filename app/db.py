from uuid import UUID, uuid4
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models import Base, RenderedModel
from app.config import settings

engine = create_engine(settings.database_url, echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(engine)


def store_model(model: str) -> str:
    with Session() as session:
        rendered_model = RenderedModel(uid=uuid4(), body=model)
        session.add(rendered_model)
        session.commit()
        ret_id = str(rendered_model.id)

    return ret_id


def retrieve_model(model_id: UUID) -> str:
    with Session() as session:
        stmt = select(RenderedModel).where(RenderedModel.id == model_id)
        return session.execute(stmt).scalar_one().body