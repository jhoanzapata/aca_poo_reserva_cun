from dataclasses import dataclass
from datetime import date, time, datetime
from typing import List, Optional
from enum import Enum
import json


class EstadoSala(Enum):
    DISPONIBLE = "disponible"
    RESERVADA = "reservada"
    MANTENIMIENTO = "mantenimiento"


class EstadoReserva(Enum):
    ACTIVA = "activa"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"


@dataclass
class Horario:
    """Value Object para manejo de horarios"""
    hora_inicio: time
    hora_fin: time

    def duracion_minutos(self) -> int:
        return (self.hora_fin.hour - self.hora_inicio.hour) * 60 + \
            (self.hora_fin.minute - self.hora_inicio.minute)

    def validar(self) -> List[str]:
        errores = []
        if self.hora_inicio >= self.hora_fin:
            errores.append("La hora de inicio debe ser anterior a la hora fin")
        if self.duracion_minutos() < 30:
            errores.append("La reserva debe durar al menos 30 minutos")
        if self.duracion_minutos() > 240:
            errores.append("La reserva no puede exceder 4 horas")
        if self.hora_inicio < time(8, 0) or self.hora_fin > time(20, 0):
            errores.append("Horario fuera del rango permitido (8:00 - 20:00)")
        return errores


@dataclass
class Estudiante:
    """Entidad Estudiante - RF10"""
    id: Optional[int]
    identificacion: str
    nombre: str
    email: Optional[str] = None
    creado_en: Optional[datetime] = None

    def validar(self) -> List[str]:
        errores = []
        if not self.identificacion.strip():
            errores.append("La identificación es obligatoria")
        if not self.nombre.strip():
            errores.append("El nombre es obligatorio")
        if len(self.identificacion) > 20:
            errores.append("La identificación no puede exceder 20 caracteres")
        return errores


@dataclass
class Sala:
    """Entidad Sala - RF1, RF2, RF9"""
    id: Optional[int]
    nombre: str
    capacidad: int
    estado: EstadoSala = EstadoSala.DISPONIBLE
    descripcion: Optional[str] = None
    horarios_disponibles: Optional[List[dict]] = None
    creado_en: Optional[datetime] = None

    def __post_init__(self):
        if self.horarios_disponibles and isinstance(self.horarios_disponibles, str):
            self.horarios_disponibles = json.loads(self.horarios_disponibles)

    def validar(self) -> List[str]:
        errores = []
        if not self.nombre.strip():
            errores.append("El nombre de la sala es obligatorio")
        if self.capacidad <= 0:
            errores.append("La capacidad debe ser mayor a 0")
        return errores

    def puede_ser_reservada(self) -> bool:
        """Verifica condiciones básicas para reserva - RF8"""
        return self.estado == EstadoSala.DISPONIBLE


@dataclass
class Reserva:
    """Agregado Root Reserva - RF3, RF4, RF5, RF6, RF7"""
    id: Optional[int]
    estudiante_id: int
    sala_id: int
    fecha_reserva: date
    hora_inicio: time
    hora_fin: time
    estado: EstadoReserva = EstadoReserva.ACTIVA
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    # Objetos relacionados (no persistidos)
    estudiante: Optional[Estudiante] = None
    sala: Optional[Sala] = None

    def validar(self) -> List[str]:
        """Valida datos básicos de la reserva"""
        errores = []
        if self.fecha_reserva < date.today():
            errores.append("No se pueden hacer reservas en fechas pasadas")

        horario = Horario(self.hora_inicio, self.hora_fin)
        errores.extend(horario.validar())

        return errores

    def cancelar(self):
        """Comportamiento de cancelación - RF7"""
        self.estado = EstadoReserva.CANCELADA
        self.actualizado_en = datetime.now()
