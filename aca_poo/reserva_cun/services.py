from typing import List, Optional
from datetime import date, time, datetime
from models import Sala, Reserva, Estudiante
from repositories import SalaRepository, ReservaRepository, EstudianteRepository


class EstudianteService:
    def __init__(self, estudiante_repo: EstudianteRepository):
        self.estudiante_repo = estudiante_repo

    def registrar_estudiante(self, identificacion: str, nombre: str, email: str = None) -> int:
        """Registra un nuevo estudiante"""
        estudiante = Estudiante(
            id=None,
            identificacion=identificacion,
            nombre=nombre,
            email=email
        )
        return self.estudiante_repo.crear(estudiante)

    def obtener_estudiante_por_identificacion(self, identificacion: str) -> Optional[Estudiante]:
        """Obtiene un estudiante por su identificación"""
        return self.estudiante_repo.obtener_por_identificacion(identificacion)


class SalaService:
    def __init__(self, sala_repo: SalaRepository):
        self.sala_repo = sala_repo

    def crear_sala(self, nombre: str, capacidad: int, descripcion: str = None) -> int:
        """Crea una nueva sala"""
        sala = Sala(
            id=None,
            nombre=nombre,
            capacidad=capacidad,
            descripcion=descripcion,
            estado='disponible'
        )
        return self.sala_repo.crear(sala)

    def listar_salas(self) -> List[Sala]:
        """Obtiene todas las salas"""
        return self.sala_repo.obtener_todas()

    def obtener_sala_por_id(self, sala_id: int) -> Optional[Sala]:
        """Obtiene una sala por su ID"""
        if not isinstance(sala_id, int) or sala_id <= 0:
            raise ValueError("ID de sala debe ser un entero positivo")
        return self.sala_repo.obtener_por_id(sala_id)


class ReservaService:
    def __init__(self, reserva_repo: ReservaRepository, sala_repo: SalaRepository,
                 estudiante_repo: EstudianteRepository):
        self.reserva_repo = reserva_repo
        self.sala_repo = sala_repo
        self.estudiante_repo = estudiante_repo

    def crear_reserva(self, estudiante_id: int, sala_id: int, fecha: date, hora_inicio: time, hora_fin: time) -> int:
        """
        Crea una nueva reserva con validaciones completas
        Returns: ID de la reserva creada
        """
        # Validar que el estudiante existe
        estudiante = self.estudiante_repo.obtener_por_id(estudiante_id)
        if not estudiante:
            raise ValueError("Estudiante no encontrado")

        # Validar que la sala existe y está disponible
        sala = self.sala_repo.obtener_por_id(sala_id)
        if not sala:
            raise ValueError("Sala no encontrada")

        if not sala.esta_disponible(fecha, hora_inicio, hora_fin):
            raise ValueError("La sala no está disponible en el horario solicitado")

        # Verificar que el estudiante no tenga otra reserva en el mismo horario
        reservas_estudiante = self.reserva_repo.obtener_por_estudiante(estudiante_id)
        for reserva in reservas_estudiante:
            if (reserva.estado == 'activa' and
                    reserva.fecha_reserva == fecha and
                    not (reserva.hora_fin <= hora_inicio or reserva.hora_inicio >= hora_fin)):
                raise ValueError("Ya tiene una reserva activa en ese horario")

        # Crear objeto reserva
        reserva = Reserva(
            id=None,
            estudiante_id=estudiante_id,
            sala_id=sala_id,
            fecha_reserva=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )

        # Crear reserva en la base de datos
        return self.reserva_repo.crear(reserva)

    def consultar_disponibilidad(self, sala_id: int, fecha: date, hora_inicio: time, hora_fin: time) -> bool:
        """Consulta la disponibilidad de una sala en un horario específico"""
        sala = self.sala_repo.obtener_por_id(sala_id)
        if not sala or sala.estado != 'disponible':
            return False

        return not self.reserva_repo._existe_reserva_conflicto(sala_id, fecha, hora_inicio, hora_fin)

    def cancelar_reserva(self, reserva_id: int, es_administrador: bool = False) -> bool:
        """Cancela una reserva existente con validaciones completas"""
        try:
            reserva = self.reserva_repo.obtener_por_id(reserva_id)
            if not reserva:
                raise ValueError("Reserva no encontrada")

            # Validar que no sea una reserva pasada
            if reserva.fecha_reserva < date.today():
                raise ValueError("No se pueden cancelar reservas pasadas")

            # Validaciones específicas para estudiantes
            if not es_administrador:
                self._validar_cancelacion_estudiante(reserva)

            # Ejecutar cancelación
            reserva.cancelar()
            self.reserva_repo.actualizar(reserva)

            # Actualizar estado de la sala
            self._actualizar_estado_sala(reserva.sala_id)

            return True

        except Exception as e:
            # Mejorar mensaje de error manteniendo la traza original
            error_msg = str(e)
            if "Reserva no encontrada" in error_msg:
                raise ValueError("Reserva no encontrada")
            else:
                raise ValueError(f"No se pudo cancelar la reserva: {error_msg}")

    def _validar_cancelacion_estudiante(self, reserva):
        """Valida reglas de negocio para cancelación de estudiantes"""
        if reserva.fecha_reserva == date.today():
            from datetime import datetime

            ahora = datetime.now().time()
            # Calcular 1 hora antes de la reserva
            hora_limite_minutos = (reserva.hora_inicio.hour * 60 + reserva.hora_inicio.minute) - 60

            if hora_limite_minutos < 0:
                hora_limite_minutos = 0

            hora_limite = time(hora_limite_minutos // 60, hora_limite_minutos % 60)

            if ahora >= hora_limite:
                raise ValueError("No se pueden cancelar reservas con menos de 1 hora de anticipación")

    def _actualizar_estado_sala(self, sala_id: int):
        """Actualiza el estado de la sala basado en reservas activas"""
        reservas_activas = self.reserva_repo.obtener_por_sala(sala_id)
        tiene_reservas_activas = any(r.estado == 'activa' for r in reservas_activas)

        if not tiene_reservas_activas:
            self.sala_repo.actualizar_estado(sala_id, 'disponible')

    def obtener_reservas_por_estudiante(self, estudiante_id: int) -> List[Reserva]:
        """Obtiene todas las reservas de un estudiante"""
        return self.reserva_repo.obtener_por_estudiante(estudiante_id)

    def obtener_reservas_por_sala(self, sala_id: int) -> List[Reserva]:
        """Obtiene todas las reservas de una sala"""
        return self.reserva_repo.obtener_por_sala(sala_id)

    def obtener_reserva_por_id(self, reserva_id: int) -> Optional[Reserva]:
        """Obtiene una reserva específica por su ID"""
        return self.reserva_repo.obtener_por_id(reserva_id)
