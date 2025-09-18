import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys

try:
    load_dotenv()
except Exception as e:
    print(f"⚠️ Avertissement : Impossible de charger le fichier .env : {e}")
    print("💡 Créez un fichier .env avec vos variables de configuration ou définissez-les dans l'environnement système")

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
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_session():
    return SessionLocal()

def execute_query(query, params=None):

    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return result.fetchall()
def ping():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

def execute_single_query(query, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        row = result.fetchone()
        return dict(row._mapping) if row else None

def execute_write(query, params=None):
    with engine.begin() as conn:
        result = conn.execute(text(query), params or {})
        try:
            return result.lastrowid
        except Exception:
            return None
