from datetime import datetime, timezone
from typing import TypeVar, Generic, Type

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as pydanticBaseModel
from sqlalchemy.orm import Session

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=pydanticBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=pydanticBaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def _filter(self, query, filter_by):
        if filter_by and isinstance(filter_by, dict):
            for key, val in filter_by.items():
                col = getattr(self.model, key)
                query = query.filter(col == val)
        return query

    def get(self, session: Session, dropped_at_filter: bool = True, **kwargs) -> ModelType:
        query = session.query(self.model)
        query = self._filter(query, kwargs)
        if dropped_at_filter:
            query = self._filter(query, dict(dropped_at=None))
        result = query.first()
        return result

    def create(self, session: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        session.flush()
        return db_obj

    def remove(self, session: Session, obj_id: int) -> ModelType:
        obj = session.query(self.model).get(obj_id)
        session.delete(obj)
        return obj

    def all(self, session: Session, dropped_at_filter: bool = True, **kwargs) -> list[ModelType]:
        query = session.query(self.model)
        query = self._filter(query, kwargs)
        if dropped_at_filter:
            query = self._filter(query, dict(dropped_at=None))
        result = query.all()
        return result

    def update(self, session: Session, args: dict, **kwargs) -> ModelType:
        query = session.query(self.model)
        query = self._filter(query, kwargs)
        result = query.update(args)
        session.flush()
        return result

    def drop(self, session: Session, **kwargs):
        result = self.update(session=session, args=dict(dropped_at=datetime.now(timezone.utc)), where=where)
        return result
