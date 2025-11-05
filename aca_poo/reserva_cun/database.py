import sqlite3
from contextlib import contextmanager
from typing import Iterator, List



class DatabaseManager:
    def __init__(self, db_path: str = "reserva_cun.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos con esquemas y datos de prueba"""
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
                    horarios_disponibles TEXT,
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

            # Índices para rendimiento - RNF6
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reservas_estudiante ON reservas(estudiante_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reservas_sala ON reservas(sala_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reservas_fecha ON reservas(fecha_reserva)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reservas_estado ON reservas(estado)')

            conn.commit()

            # Poblar datos iniciales
            self._poblar_datos_iniciales(conn)

    def _poblar_datos_iniciales(self, conn):
        """Pobla la base de datos con datos de prueba iniciales"""
        try:
            cursor = conn.cursor()

            # Verificar si ya existen datos
            cursor.execute("SELECT COUNT(*) FROM estudiantes")
            if cursor.fetchone()[0] == 0:
                # Estudiantes de prueba
                estudiantes = [
                    ('1001', 'Ana García López', 'ana.garcia@cun.edu.co'),
                    ('1002', 'Carlos Rodríguez Méndez', 'carlos.rodriguez@cun.edu.co'),
                    ('1003', 'María Fernández Castro', 'maria.fernandez@cun.edu.co'),
                    ('1004', 'José Martínez Ruiz', 'jose.martinez@cun.edu.co'),
                    ('1005', 'Laura González Silva', 'laura.gonzalez@cun.edu.co')
                ]
                cursor.executemany(
                    "INSERT INTO estudiantes (identificacion, nombre, email) VALUES (?, ?, ?)",
                    estudiantes
                )

                # Salas de prueba
                salas = [
                    ('Sala Individual A', 4, 'disponible', 'Sala para estudio individual y concentrado'),
                    ('Sala Grupal B', 6, 'disponible', 'Sala para trabajos en equipo pequeños'),
                    ('Sala Conferencias C', 12, 'disponible', 'Sala para presentaciones y grupos grandes'),
                    ('Sala Silenciosa D', 4, 'disponible', 'Sala de absoluto silencio para estudio'),
                    ('Sala Colaborativa E', 8, 'mantenimiento', 'Sala con equipos multimedia - En mantenimiento')
                ]
                cursor.executemany(
                    "INSERT INTO salas (nombre, capacidad, estado, descripcion) VALUES (?, ?, ?, ?)",
                    salas
                )

                conn.commit()
                print("✅ Datos iniciales cargados correctamente")

        except Exception as e:
            print(f"⚠️  No se pudieron cargar datos iniciales: {e}")

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Context manager para manejo automático de conexiones"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")  # Habilitar claves foráneas
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

    def fetch_all(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
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