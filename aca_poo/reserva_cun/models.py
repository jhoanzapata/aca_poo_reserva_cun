from dataclasses import dataclass
from datetime import date, time, datetime
from typing import List, Optional
import json


@dataclass
class Estudiante:
    id: Optional[int]
    identificacion: str
    nombre: str
    email: Optional[str] = None
    creado_en: Optional[datetime] = None

    def validar(self) -> List[str]:
        """Valida los datos del estudiante"""
        errores = []
        if not self.identificacion.strip():
            errores.append("La identificación es obligatoria")
        if not self.nombre.strip():
            errores.append("El nombre es obligatorio")
        if len(self.identificacion) > 20:
            errores.append("La identificación no puede exceder 20 caracteres")
        return errores


from dataclasses import dataclass
from datetime import date, time, datetime
from typing import List, Optional
import json


@dataclass
class Sala:
    id: Optional[int]
    nombre: str
    capacidad: int
    estado: str = "disponible"
    descripcion: Optional[str] = None
    horarios_disponibles: Optional[List[dict]] = None
    creado_en: Optional[datetime] = None

    def __post_init__(self):
        if self.horarios_disponibles and isinstance(self.horarios_disponibles, str):
            self.horarios_disponibles = json.loads(self.horarios_disponibles)

    def validar(self) -> List[str]:
        """Valida los datos de la sala"""
        errores = []
        if not self.nombre.strip():
            errores.append("El nombre de la sala es obligatorio")
        if self.capacidad <= 0:
            errores.append("La capacidad debe ser mayor a 0")
        if self.estado not in ['disponible', 'reservada', 'mantenimiento']:
            errores.append("Estado inválido")
        return errores

    def esta_disponible(self, fecha: date, hora_inicio: time, hora_fin: time) -> bool:
        """Verifica si la sala está disponible en el horario solicitado"""
        if self.estado != 'disponible':
            return False

        # Validar que la hora de inicio sea antes de la hora fin
        if hora_inicio >= hora_fin:
            return False

        # Validar horario dentro del rango permitido (8:00 - 20:00)
        if hora_inicio < time(8, 0) or hora_fin > time(20, 0):
            return False

        # Validar que no sea una fecha pasada
        if fecha < date.today():
            return False

        return True


@dataclass
class Reserva:
    id: Optional[int]
    estudiante_id: int
    sala_id: int
    fecha_reserva: date
    hora_inicio: time
    hora_fin: time
    estado: str = "activa"
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    # Relaciones (no persistidas en DB)
    estudiante: Optional[Estudiante] = None
    sala: Optional[Sala] = None

    def validar(self) -> List[str]:
        """Valida los datos de la reserva"""
        errores = []
        if self.fecha_reserva < date.today():
            errores.append("No se pueden hacer reservas en fechas pasadas")
        if self.hora_inicio >= self.hora_fin:
            errores.append("La hora de inicio debe ser anterior a la hora fin")
        if not (time(8, 0) <= self.hora_inicio <= time(20, 0)):
            errores.append("Horario fuera del rango permitido (8:00 - 20:00)")
        return errores

    def cancelar(self):
        """Cancela la reserva"""
        self.estado = 'cancelada'
        self.actualizado_en = datetime.now()
