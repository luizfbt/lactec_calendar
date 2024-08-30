from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.utils import root_path
import os

db_path = os.path.join(root_path, 'calendar.db')


class DbType(Enum):
    POSTGRESQL = 1
    SQLITE = 2

db_type = DbType.SQLITE

if db_type == DbType.SQLITE:
    db_url = f'sqlite:///{db_path}'
    connect_args = {'check_same_thread': False}
    engine = create_engine(db_url, 
                           connect_args=connect_args)
elif db_type == DbType.POSTGRESQL:
    db_url = 'postgresql://user:password@localhost/DatabaseName'
    engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, 
                            autoflush=False, 
                            bind=engine)
Base = declarative_base()
