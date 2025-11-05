import json
from datetime import datetime, date, time
from typing import List, Optional

from models import (
    Sala,
    Reserva,
    Estudiante,
    EstadoSala,
    EstadoReserva,
)


class BaseRepository:
    """Clase base para todos los repositorios."""

    def __init__(self, db_manager):
        self.db = db_manager


class SalaRepository(BaseRepository):
    """Maneja operaciones CRUD para salas."""

    def crear(self, sala: Sala) -> int:
        """Crea una nueva sala - RF1"""
        errores = sala.validar()
        if errores:
            raise ValueError(f"Errores de validación: {', '.join(errores)}")

        horarios_json = (
            json.dumps(sala.horarios_disponibles)
            if sala.horarios_disponibles
            else None
        )

        query = """
            INSERT INTO salas (nombre, capacidad, estado, descripcion, horarios_disponibles)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.db.execute_query(
            query,
            (
                sala.nombre,
                sala.capacidad,
                sala.estado.value,
                sala.descripcion,
                horarios_json,
            ),
        )
        return cursor.lastrowid

    def obtener_por_id(self, sala_id: int) -> Optional[Sala]:
        """Obtiene una sala por su ID."""
        query = "SELECT * FROM salas WHERE id = ?"
        row = self.db.fetch_one(query, (sala_id,))
        return self._row_to_sala(row) if row else None

    def obtener_todas(self) -> List[Sala]:
        """Obtiene todas las salas - RF9."""
        query = "SELECT * FROM salas ORDER BY nombre"
        rows = self.db.fetch_all(query)
        return [self._row_to_sala(row) for row in rows]

    def obtener_disponibles(self) -> List[Sala]:
        """Obtiene solo las salas disponibles."""
        query = "SELECT * FROM salas WHERE estado = 'disponible' ORDER BY nombre"
        rows = self.db.fetch_all(query)
        return [self._row_to_sala(row) for row in rows]

    def actualizar_estado(self, sala_id: int, estado: EstadoSala) -> None:
        """Actualiza el estado de una sala."""
        query = "UPDATE salas SET estado = ? WHERE id = ?"
        self.db.execute_query(query, (estado.value, sala_id))

    def actualizar(self, sala: Sala) -> bool:
        """Actualiza una sala existente."""
        query = """
            UPDATE salas 
            SET nombre = ?, capacidad = ?, estado = ?, descripcion = ?, 
                horarios_disponibles = ?
            WHERE id = ?
        """
        horarios_json = (
            json.dumps(sala.horarios_disponibles)
            if sala.horarios_disponibles
            else None
        )

        try:
            self.db.execute_query(
                query,
                (
                    sala.nombre,
                    sala.capacidad,
                    sala.estado.value,
                    sala.descripcion,
                    horarios_json,
                    sala.id,
                ),
            )
            return True
        except Exception:
            return False

    def eliminar(self, sala_id: int) -> bool:
        """Elimina una sala por ID."""
        query = "DELETE FROM salas WHERE id = ?"
        try:
            self.db.execute_query(query, (sala_id,))
            return True
        except Exception:
            return False

    def _row_to_sala(self, row) -> Sala:
        """Convierte una fila de la DB a objeto Sala."""
        return Sala(
            id=row["id"],
            nombre=row["nombre"],
            capacidad=row["capacidad"],
            estado=EstadoSala(row["estado"]),
            descripcion=row["descripcion"],
            horarios_disponibles=row["horarios_disponibles"],
            creado_en=(
                datetime.fromisoformat(row["creado_en"])
                if row["creado_en"]
                else None
            ),
        )


class ReservaRepository(BaseRepository):
    """Maneja operaciones CRUD para reservas."""

    def crear(self, reserva: Reserva) -> int:
        """Crea una nueva reserva - RF3"""
        errores = reserva.validar()
        if errores:
            raise ValueError(f"Errores de validación: {', '.join(errores)}")

        if self._existe_reserva_conflicto(
                reserva.sala_id,
                reserva.fecha_reserva,
                reserva.hora_inicio,
                reserva.hora_fin,
        ):
            raise ValueError("Ya existe una reserva para esta sala en el mismo horario")

        query = """
            INSERT INTO reservas 
            (estudiante_id, sala_id, fecha_reserva, hora_inicio, hora_fin, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.execute_query(
            query,
            (
                reserva.estudiante_id,
                reserva.sala_id,
                reserva.fecha_reserva.isoformat(),
                reserva.hora_inicio.isoformat(),
                reserva.hora_fin.isoformat(),
                reserva.estado.value,
            ),
        )
        return cursor.lastrowid

    def _existe_reserva_conflicto(
            self,
            sala_id: int,
            fecha: date,
            hora_inicio: time,
            hora_fin: time,
            excluir_reserva_id: Optional[int] = None,
    ) -> bool:
        """Verifica solapamiento de horarios - RF8"""
        query = """
            SELECT COUNT(*) as count FROM reservas 
            WHERE sala_id = ? 
              AND fecha_reserva = ? 
              AND estado = 'activa'
              AND hora_inicio < ? 
              AND hora_fin > ?
        """
        params = [
            sala_id,
            fecha.isoformat(),
            hora_fin.isoformat(),
            hora_inicio.isoformat(),
        ]

        if excluir_reserva_id:
            query += " AND id != ?"
            params.append(excluir_reserva_id)

        row = self.db.fetch_one(query, tuple(params))
        return row["count"] > 0 if row else False

    def obtener_por_id(self, reserva_id: int) -> Optional[Reserva]:
        """Obtiene una reserva por su ID."""
        query = "SELECT * FROM reservas WHERE id = ?"
        row = self.db.fetch_one(query, (reserva_id,))
        return self._row_to_reserva(row) if row else None

    def obtener_por_sala(self, sala_id: int) -> List[Reserva]:
        """Obtiene todas las reservas de una sala - RF4"""
        query = """
            SELECT r.*, e.nombre as estudiante_nombre, s.nombre as sala_nombre
            FROM reservas r
            JOIN estudiantes e ON r.estudiante_id = e.id
            JOIN salas s ON r.sala_id = s.id
            WHERE r.sala_id = ?
            ORDER BY r.fecha_reserva, r.hora_inicio
        """
        rows = self.db.fetch_all(query, (sala_id,))
        return [self._row_to_reserva(row) for row in rows]

    def obtener_por_estudiante(self, estudiante_id: int) -> List[Reserva]:
        """Obtiene todas las reservas de un estudiante - RF5"""
        query = """
            SELECT r.*, e.nombre as estudiante_nombre, s.nombre as sala_nombre
            FROM reservas r
            JOIN estudiantes e ON r.estudiante_id = e.id
            JOIN salas s ON r.sala_id = s.id
            WHERE r.estudiante_id = ?
            ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC
        """
        rows = self.db.fetch_all(query, (estudiante_id,))
        return [self._row_to_reserva(row) for row in rows]

    def obtener_activas_por_sala_y_fecha(
            self, sala_id: int, fecha: date
    ) -> List[Reserva]:
        """Obtiene reservas activas por sala y fecha."""
        query = """
            SELECT * FROM reservas 
            WHERE sala_id = ? 
              AND fecha_reserva = ? 
              AND estado = 'activa'
            ORDER BY hora_inicio
        """
        rows = self.db.fetch_all(query, (sala_id, fecha.isoformat()))
        return [self._row_to_reserva(row) for row in rows]

    def actualizar(self, reserva: Reserva) -> None:
        """Actualiza una reserva existente - RF6, RF7"""
        query = """
            UPDATE reservas 
            SET estudiante_id = ?, sala_id = ?, fecha_reserva = ?, 
                hora_inicio = ?, hora_fin = ?, estado = ?, 
                actualizado_en = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        self.db.execute_query(
            query,
            (
                reserva.estudiante_id,
                reserva.sala_id,
                reserva.fecha_reserva.isoformat(),
                reserva.hora_inicio.isoformat(),
                reserva.hora_fin.isoformat(),
                reserva.estado.value,
                reserva.id,
            ),
        )

    def _row_to_reserva(self, row) -> Reserva:
        """Convierte fila a objeto Reserva con relaciones."""
        estudiante_obj = (
            Estudiante(
                id=row["estudiante_id"],
                identificacion="",
                nombre=row.get("estudiante_nombre", "N/A"),
            )
            if "estudiante_id" in row
            else None
        )

        sala_obj = (
            Sala(
                id=row["sala_id"],
                nombre=row.get("sala_nombre", "N/A"),
                capacidad=0,
                estado=EstadoSala.DISPONIBLE,
            )
            if "sala_id" in row
            else None
        )

        return Reserva(
            id=row["id"],
            estudiante_id=row["estudiante_id"],
            sala_id=row["sala_id"],
            fecha_reserva=date.fromisoformat(row["fecha_reserva"]),
            hora_inicio=time.fromisoformat(row["hora_inicio"]),
            hora_fin=time.fromisoformat(row["hora_fin"]),
            estado=EstadoReserva(row["estado"]),
            creado_en=(
                datetime.fromisoformat(row["creado_en"])
                if row["creado_en"]
                else None
            ),
            actualizado_en=(
                datetime.fromisoformat(row["actualizado_en"])
                if row["actualizado_en"]
                else None
            ),
            estudiante=estudiante_obj,
            sala=sala_obj,
        )


class EstudianteRepository(BaseRepository):
    """Maneja operaciones CRUD para estudiantes."""

    def crear(self, estudiante: Estudiante) -> int:
        """Crea un nuevo estudiante - RF10"""
        errores = estudiante.validar()
        if errores:
            raise ValueError(f"Errores de validación: {', '.join(errores)}")

        query = """
            INSERT INTO estudiantes (identificacion, nombre, email)
            VALUES (?, ?, ?)
        """
        cursor = self.db.execute_query(
            query,
            (estudiante.identificacion, estudiante.nombre, estudiante.email),
        )
        return cursor.lastrowid

    def obtener_por_id(self, estudiante_id: int) -> Optional[Estudiante]:
        """Obtiene un estudiante por su ID."""
        query = "SELECT * FROM estudiantes WHERE id = ?"
        row = self.db.fetch_one(query, (estudiante_id,))
        return self._row_to_estudiante(row) if row else None

    def obtener_por_identificacion(self, identificacion: str) -> Optional[Estudiante]:
        """Obtiene un estudiante por su identificación."""
        query = "SELECT * FROM estudiantes WHERE identificacion = ?"
        row = self.db.fetch_one(query, (identificacion,))
        return self._row_to_estudiante(row) if row else None

    def obtener_todos(self) -> List[Estudiante]:
        """Obtiene todos los estudiantes."""
        query = "SELECT * FROM estudiantes ORDER BY nombre"
        rows = self.db.fetch_all(query)
        return [self._row_to_estudiante(row) for row in rows]

    def _row_to_estudiante(self, row) -> Estudiante:
        """Convierte fila a objeto Estudiante."""
        return Estudiante(
            id=row["id"],
            identificacion=row["identificacion"],
            nombre=row["nombre"],
            email=row["email"],
            creado_en=(
                datetime.fromisoformat(row["creado_en"])
                if row["creado_en"]
                else None
            ),
        )