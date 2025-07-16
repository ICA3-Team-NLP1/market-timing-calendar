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

    # 스키마 설정 제거 - SQL 초기화 스크립트와 일치시키기 위함
    # 모든 테이블이 기본 스키마(public)를 사용하도록 통일
    __table_args__ = {"extend_existing": True}

    @declared_attr
    def __tablename__(cls) -> str:
        """
        ex) -> LevelFeature
        :return: level_feature
        """
        pattern = re.compile(r"(?<!^)(?=[A-Z])")
        return pattern.sub("_", cls.__name__).lower()
