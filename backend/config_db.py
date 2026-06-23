import os
import logging
from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
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
        if self._pool is not None:
            return
        requeridas = {"DB_NAME": os.getenv("DB_NAME"), "DB_USER": os.getenv("DB_USER")}
        faltantes = [k for k, v in requeridas.items() if not v]
        if faltantes:
            raise ValueError(f"Error crítico: faltan variables en .env: {', '.join(faltantes)}")

        self._pool = ThreadedConnectionPool(
            1, 15,
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            dbname=requeridas["DB_NAME"],
            user=requeridas["DB_USER"],
            password=os.getenv("DB_PASSWORD"),
            cursor_factory=RealDictCursor,
            connect_timeout=10,
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
            logger.error(f"Rollback ejecutado: {type(e).__name__}: {e}")
            raise
        finally:
            cursor.close()
            self._pool.putconn(conexion)


db = ConexionDB()
