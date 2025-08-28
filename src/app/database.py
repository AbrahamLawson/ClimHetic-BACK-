import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()


DIALECT = os.getenv("DB_DIALECT", "mysql")
USER = os.getenv("DB_USER")
PWD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST", "localhost")
PORT = os.getenv("DB_PORT", "3306")
NAME = os.getenv("DB_NAME")
USE_SSL = os.getenv("DB_SSL", "0") == "1"

DRIVER = "pymysql"  

DATABASE_URL = f"{DIALECT}+{DRIVER}://{USER}:{PWD}@{HOST}:{PORT}/{NAME}?charset=utf8mb4"

connect_args = {}
if USE_SSL:
    connect_args["ssl"] = {"ssl_mode": "REQUIRED"}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args=connect_args,
    # echo=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_session():
    return SessionLocal()

def ping():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
