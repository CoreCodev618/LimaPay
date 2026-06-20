import os
import logging
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.WARNING, format="%(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("limapay.db")
logger.setLevel(logging.DEBUG)

class ConexionDB:
    _instancia = None
    _pool = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def conectar(self):
        if self._pool is None:
            db_name = os.getenv("DB_NAME")
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = int(os.getenv("DB_PORT", 5432))
            if not db_name:
                raise ValueError("Error crítico: DB_NAME no configurado en .env")
            if not db_user:
                raise ValueError("Error crítico: DB_USER no configurado en .env")
            logger.debug(f"Conectando a PostgreSQL: host={db_host} port={db_port} db={db_name} user={db_user}")
            self._pool = ThreadedConnectionPool(
                1, 15,
                host=db_host,
                port=db_port,
                dbname=db_name,
                user=db_user,
                password=db_password,
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
            logger.info("Pool de conexiones PostgreSQL creado exitosamente")

    @contextmanager
    def obtener_cursor(self):
        self.conectar()
        conexion = self._pool.getconn()
        cursor = conexion.cursor()
        try:
            cursor.execute("SET search_path TO public;")
            yield cursor
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            logger.error(f"Error en transacción BD, rollback ejecutado: {type(e).__name__}: {e}")
            raise
        finally:
            cursor.close()
            self._pool.putconn(conexion)

db = ConexionDB()