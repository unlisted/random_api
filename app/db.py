from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

engine = create_engine("postgresql+psycopg2://test:test@postgres:5432/test", echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(engine)