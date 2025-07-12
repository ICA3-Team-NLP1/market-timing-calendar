import json

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker

from .config import DBConnection


class _SessionGenerator:
    _session = None

    def __init__(self, session: sessionmaker):
        self._session = session

    def __call__(self):
        try:
            yield self._session()
        finally:
            self._session().close()

    def __enter__(self):
        """Context manager 진입"""
        self._current_session = self._session()
        return self._current_session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        if hasattr(self, '_current_session'):
            self._current_session.close()


class SQLAlchemy:
    def __init__(self, app=None, **kwargs):
        self._engine: Engine | None = None
        self._session: sessionmaker | None = None
        if app is not None:
            self.init_db(**kwargs)
            self.startup()

    def init_db(self, db_info: DBConnection):
        """
        DB 초기화 함수
        """
        database_url = db_info.SQLALCHEMY_DATABASE_URL
        pool_recycle = db_info.SQLALCHEMY_POOL_RECYCLE
        echo = db_info.SQLALCHEMY_ECHO
        pool_size = db_info.POOL_SIZE
        max_overflow = db_info.MAX_OVERFLOW
        self._engine = create_engine(
            database_url,
            echo=echo,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
            pool_size=pool_size,
            max_overflow=max_overflow,
            json_serializer=lambda x: json.dumps(x, ensure_ascii=False),
        )
        self._session = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    def startup(self):
        self._engine.connect()

    def shutdown(self):
        self.clear_session()

    def clear_session(self):
        self._session.close_all()
        self._engine.dispose()

    @property
    def session(self):
        return _SessionGenerator(self._session)

    @property
    def engine(self):
        return self._engine


db = SQLAlchemy()
