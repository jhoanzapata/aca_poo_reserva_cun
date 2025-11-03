import sqlite3
from contextlib import contextmanager
from typing import Iterator
import os


class DatabaseManager:
    def __init__(self, db_path: str = "reserva_cun.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos con esquemas necesarios"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Tabla de estudiantes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estudiantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identificacion TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    email TEXT,
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de salas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS salas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    capacidad INTEGER NOT NULL CHECK (capacidad > 0),
                    estado TEXT DEFAULT 'disponible' CHECK (estado IN ('disponible', 'reservada', 'mantenimiento')),
                    descripcion TEXT,
                    horarios_disponibles TEXT, -- JSON string con horarios
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de reservas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reservas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estudiante_id INTEGER NOT NULL,
                    sala_id INTEGER NOT NULL,
                    fecha_reserva DATE NOT NULL,
                    hora_inicio TIME NOT NULL,
                    hora_fin TIME NOT NULL,
                    estado TEXT DEFAULT 'activa' CHECK (estado IN ('activa', 'cancelada', 'completada')),
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id) ON DELETE CASCADE,
                    FOREIGN KEY (sala_id) REFERENCES salas (id) ON DELETE CASCADE,
                    UNIQUE(sala_id, fecha_reserva, hora_inicio)
                )
            ''')

            # Índices para mejorar performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reservas_estudiante ON reservas(estudiante_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reservas_sala ON reservas(sala_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reservas_fecha ON reservas(fecha_reserva)')

            conn.commit()

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Context manager para manejo automático de conexiones"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Ejecuta una query y retorna el cursor"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def fetch_all(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Ejecuta query y retorna todos los resultados"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query: str, params: tuple = ()) -> sqlite3.Row | None:
        """Ejecuta query y retorna un único resultado"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()


def poblar_datos_prueba(self):
    """Pobla la base de datos con datos de prueba para desarrollo"""
    try:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Verificar si ya existen datos
            cursor.execute("SELECT COUNT(*) FROM estudiantes")
            if cursor.fetchone()[0] == 0:
                # Insertar estudiantes de prueba
                estudiantes = [
                    ('1001', 'Ana García', 'ana@universidad.edu'),
                    ('1002', 'Carlos López', 'carlos@universidad.edu'),
                    ('1003', 'María Rodríguez', 'maria@universidad.edu')
                ]

                cursor.executemany(
                    "INSERT INTO estudiantes (identificacion, nombre, email) VALUES (?, ?, ?)",
                    estudiantes
                )

                # Insertar salas de prueba
                salas = [
                    ('Sala A', 4, 'disponible', 'Sala individual para estudio concentrado'),
                    ('Sala B', 6, 'disponible', 'Sala grupal para trabajos en equipo'),
                    ('Sala C', 8, 'disponible', 'Sala grande para presentaciones')
                ]

                cursor.executemany(
                    "INSERT INTO salas (nombre, capacidad, estado, descripcion) VALUES (?, ?, ?, ?)",
                    salas
                )

                conn.commit()
                print("✅ Datos de prueba insertados correctamente")

    except Exception as e:
        print(f"❌ Error al insertar datos de prueba: {e}")
