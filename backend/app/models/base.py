import re

from sqlalchemy import Column, Integer, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declared_attr


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp(), default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp(), default=func.current_timestamp()
    )
    dropped_at = Column(TIMESTAMP, nullable=True)
    __table_args__ = {"schema": "public", "extend_existing": True}

    @declared_attr
    def __tablename__(cls) -> str:
        """
        ex) -> LevelFeature
        :return: level_feature
        """
        pattern = re.compile(r"(?<!^)(?=[A-Z])")
        return pattern.sub("_", cls.__name__).lower()
