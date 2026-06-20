import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class ConexionDB:
    _instancia=None
    _pool=None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia=super().__new__(cls)
        return cls._instancia

    def conectar(self):
        if self._pool is None:
            try:
                self._pool=psycopg2.pool.SimpleConnectionPool(
                    1,15,
                    host=os.getenv("DB_HOST","localhost"),
                    port=int(os.getenv("DB_PORT",5432)),
                    dbname=os.getenv("DB_NAME","postgres"),
                    user=os.getenv("DB_USER","postgres"),
                    password=os.getenv("DB_PASSWORD",""),
                    cursor_factory=RealDictCursor,
                    connect_timeout=10
                )
            except psycopg2.OperationalError as e:
                raise

    @contextmanager
    def obtener_cursor(self):
        self.conectar()
        conexion=self._pool.getconn()
        conexion.autocommit=False
        cursor=conexion.cursor()
        try:
            yield cursor
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            cursor.close()
            self._pool.putconn(conexion)

    def cerrar(self):
        if self._pool:
            self._pool.closeall()

db=ConexionDB()
