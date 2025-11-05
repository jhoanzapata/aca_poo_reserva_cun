from typing import List, Optional, TYPE_CHECKING
from datetime import date, time, datetime, timedelta
import json
import sqlite3

# Importaciones de modelos y repositorios
from models import Sala, Reserva, Estudiante
from repositories import SalaRepository, ReservaRepository, EstudianteRepository, BaseRepository

from models import EstadoSala  # ← AGREGA ESTO AL INICIO

# Importación para evitar dependencias circulares
if TYPE_CHECKING:
    from services import ReservaService


class PoliticaCancelacion:
    """Define políticas de cancelación de reservas - RF7"""

    def puede_cancelar_estudiante(self, reserva: Reserva) -> bool:
        """Política para estudiantes: 1 hora de anticipación mínima"""
        if reserva.fecha_reserva < date.today():
            return False

        if reserva.fecha_reserva == date.today():
            ahora = datetime.now()
            inicio_reserva = datetime.combine(reserva.fecha_reserva, reserva.hora_inicio)
            return (inicio_reserva - ahora) >= timedelta(hours=1)

        return True

    def puede_cancelar_administrador(self, reserva: Reserva) -> bool:
        """Política para administradores: siempre pueden cancelar"""
        return True


class EstudianteService:
    """Servicio para gestión de estudiantes - RF10"""

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

    def obtener_estudiante_por_id(self, estudiante_id: int) -> Optional[Estudiante]:
        """Obtiene un estudiante por su ID"""
        return self.estudiante_repo.obtener_por_id(estudiante_id)


class SalaService:
    """Servicio para gestión de salas - RF1, RF2, RF9"""

    def __init__(self, sala_repo: SalaRepository, reserva_service: Optional['ReservaService'] = None):
        self.sala_repo = sala_repo
        self.reserva_service = reserva_service

    def listar_salas(self) -> List[Sala]:
        """Obtiene todas las salas"""
        return self.sala_repo.obtener_todas()

    def listar_salas_disponibles(self) -> List[Sala]:
        """Obtiene solo las salas disponibles"""
        return self.sala_repo.obtener_disponibles()

    def obtener_sala_por_id(self, sala_id: int) -> Optional[Sala]:
        """Obtiene una sala por su ID"""
        if not isinstance(sala_id, int) or sala_id <= 0:
            raise ValueError("ID de sala debe ser un entero positivo")
        return self.sala_repo.obtener_por_id(sala_id)

    def obtener_estado_salas(self) -> List[dict]:
        """Obtiene el estado detallado de todas las salas - RF9"""
        salas = self.sala_repo.obtener_todas()
        estado_salas = []

        for sala in salas:
            estado_salas.append({
                'sala': sala,
                'estado': sala.estado,
                'puede_reservar': sala.estado == 'disponible'
            })

        return estado_salas

    def actualizar_sala(self, sala_id: int, nombre: str, capacidad: int,
                        descripcion: str = None, estado: str = None) -> bool:
        sala_actual = self.sala_repo.obtener_por_id(sala_id)
        if not sala_actual:
            raise ValueError("Sala no encontrada")

        nuevo_estado = sala_actual.estado
        if estado and estado.lower() in ['disponible', 'reservada', 'mantenimiento']:
            nuevo_estado = EstadoSala(estado.lower())

        sala_actualizada = Sala(
            id=sala_id,
            nombre=nombre,
            capacidad=capacidad,
            descripcion=descripcion or sala_actual.descripcion,
            estado=nuevo_estado,
            horarios_disponibles=sala_actual.horarios_disponibles,
            creado_en=sala_actual.creado_en
        )

        return self.sala_repo.actualizar(sala_actualizada)

    def eliminar_sala(self):
        """Elimina una sala existente"""
        try:
            print("\n--- ELIMINAR SALA ---")
            self.listar_salas()
            sala_id = int(input("ID de la sala a eliminar: "))

            # Confirmación
            sala = self.sala_service.obtener_sala_por_id(sala_id)
            if not sala:
                self.mostrar_error("Sala no encontrada")
                return

            print(f"\n⚠️  Está a punto de eliminar la sala: {sala.nombre}")
            print("Esta acción no se puede deshacer.")

            confirmar = input("¿Está seguro de que desea eliminar esta sala? (s/n): ").lower().strip()
            if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                self.mostrar_exito("Eliminación cancelada")
                return

            self.sala_service.eliminar_sala(sala_id)
            self.mostrar_exito("Sala eliminada exitosamente")

        except ValueError as e:
            self.mostrar_error(f"ID inválido: {e}")
        except Exception as e:
            self.mostrar_error(f"Error al eliminar sala: {e}")
        finally:
            self.pausar()

    def crear_sala(self, nombre: str, capacidad: int, descripcion: str = None) -> int:
        """Crea una nueva sala - RF1"""
        sala = Sala(
            id=None,
            nombre=nombre,
            capacidad=capacidad,
            descripcion=descripcion,
            estado=EstadoSala.DISPONIBLE,  # ← ENUM CORRECTO
            horarios_disponibles=None
        )
        return self.sala_repo.crear(sala)

    def listar_salas(self) -> List[Sala]:
        """Obtiene todas las salas"""
        return self.sala_repo.obtener_todas()

    def listar_salas_disponibles(self) -> List[Sala]:
        """Obtiene solo las salas disponibles"""
        return self.sala_repo.obtener_disponibles()

    def obtener_sala_por_id(self, sala_id: int) -> Optional[Sala]:
        """Obtiene una sala por su ID"""
        if not isinstance(sala_id, int) or sala_id <= 0:
            raise ValueError("ID de sala debe ser un entero positivo")
        return self.sala_repo.obtener_por_id(sala_id)

    def obtener_estado_salas(self) -> List[dict]:
        """Obtiene el estado detallado de todas las salas - RF9"""
        salas = self.sala_repo.obtener_todas()
        estado_salas = []

        for sala in salas:
            estado_salas.append({
                'sala': sala,
                'estado': sala.estado,
                'puede_reservar': sala.estado == 'disponible'
            })

        return estado_salas

    def actualizar_sala(self, sala_id: int, nombre: str, capacidad: int,
                        descripcion: str = None, estado: str = None) -> bool:
        """Actualiza una sala existente"""
        from models import EstadoSala

        sala_actual = self.sala_repo.obtener_por_id(sala_id)
        if not sala_actual:
            raise ValueError("Sala no encontrada")

        # Convertir string a Enum
        nuevo_estado = sala_actual.estado
        if estado and estado.lower() in ['disponible', 'reservada', 'mantenimiento']:
            nuevo_estado = EstadoSala(estado.lower())

        sala_actualizada = Sala(
            id=sala_id,
            nombre=nombre,
            capacidad=capacidad,
            descripcion=descripcion or sala_actual.descripcion,
            estado=nuevo_estado,
            horarios_disponibles=sala_actual.horarios_disponibles,
            creado_en=sala_actual.creado_en
        )

        return self.sala_repo.actualizar(sala_actualizada)

    def eliminar_sala(self, sala_id: int) -> bool:
        """Elimina una sala si no tiene reservas activas"""
        if not isinstance(sala_id, int) or sala_id <= 0:
            raise ValueError("ID de sala debe ser un entero positivo")

        # Verificar si hay reservas activas para esta sala
        if self.reserva_service:
            reservas = self.reserva_service.obtener_reservas_por_sala(sala_id)
            reservas_activas = [r for r in reservas if r.estado == 'activa']

            if reservas_activas:
                raise ValueError("No se puede eliminar la sala porque tiene reservas activas")

        return self.sala_repo.eliminar(sala_id)

    def obtener_salas_con_reservas(self) -> List[dict]:
        """Obtiene información de salas con conteo de reservas activas"""
        salas = self.sala_repo.obtener_todas()
        salas_info = []

        for sala in salas:
            # Contar reservas activas para esta sala
            reservas_count = 0
            if self.reserva_service:
                try:
                    reservas = self.reserva_service.obtener_reservas_por_sala(sala.id)
                    reservas_count = len([r for r in reservas if r.estado == 'activa'])
                except:
                    pass

            salas_info.append({
                'sala': sala,
                'reservas_activas': reservas_count,
                'puede_eliminar': reservas_count == 0
            })

        return salas_info

    def obtener_salas_con_reservas(self) -> List[dict]:
        """Obtiene información de salas con conteo de reservas activas"""
        salas = self.sala_repo.obtener_todas()
        salas_info = []

        for sala in salas:
            # Contar reservas activas para esta sala
            reservas_count = 0
            if self.reserva_service:
                try:
                    reservas = self.reserva_service.obtener_reservas_por_sala(sala.id)
                    reservas_count = len([r for r in reservas if r.estado == 'activa'])
                except:
                    pass

            salas_info.append({
                'sala': sala,
                'reservas_activas': reservas_count,
                'puede_eliminar': reservas_count == 0
            })

        return salas_info


class ReservaService:
    """Servicio para gestión de reservas - RF3, RF4, RF5, RF6, RF7, RF8"""

    def __init__(self, reserva_repo: ReservaRepository, sala_repo: SalaRepository,
                 estudiante_repo: EstudianteRepository):
        self.reserva_repo = reserva_repo
        self.sala_repo = sala_repo
        self.estudiante_repo = estudiante_repo
        self.politica_cancelacion = PoliticaCancelacion()

    def crear_reserva(self, estudiante_id: int, sala_id: int, fecha: date,
                      hora_inicio: time, hora_fin: time) -> int:
        """
        Crea una nueva reserva con validaciones completas - RF3
        Returns: ID de la reserva creada
        """
        # Validar que el estudiante existe
        estudiante = self.estudiante_repo.obtener_por_id(estudiante_id)
        if not estudiante:
            raise ValueError("Estudiante no encontrado")

        # Validar que la sala existe
        sala = self.sala_repo.obtener_por_id(sala_id)
        if not sala:
            raise ValueError("Sala no encontrada")

        # Validar que la sala puede ser reservada
        if sala.estado != 'disponible':
            raise ValueError(f"La sala no está disponible para reservas. Estado: {sala.estado}")

        # Validar horario
        if hora_inicio >= hora_fin:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")

        # Validar rango horario (8:00 - 20:00)
        if hora_inicio < time(8, 0) or hora_fin > time(20, 0):
            raise ValueError("El horario de reserva debe estar entre 8:00 y 20:00")

        # Validar duración mínima (30 minutos)
        duracion_minutos = (hora_fin.hour - hora_inicio.hour) * 60 + (hora_fin.minute - hora_inicio.minute)
        if duracion_minutos < 30:
            raise ValueError("La reserva debe tener al menos 30 minutos de duración")

        # Validar duración máxima (4 horas)
        if duracion_minutos > 240:
            raise ValueError("La reserva no puede exceder 4 horas de duración")

        # Validar fecha
        if fecha < date.today():
            raise ValueError("No se pueden hacer reservas en fechas pasadas")

        # Validar disponibilidad - RF8
        if not self.consultar_disponibilidad(sala_id, fecha, hora_inicio, hora_fin):
            raise ValueError("La sala no está disponible en ese horario")

        # Validar que el estudiante no tenga otra reserva en el mismo horario
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
            hora_fin=hora_fin,
            estado='activa'
        )

        # Crear reserva en la base de datos
        reserva_id = self.reserva_repo.crear(reserva)

        # Actualizar estado de la sala si es necesario
        self._actualizar_estado_sala(sala_id)

        return reserva_id

    def consultar_disponibilidad(self, sala_id: int, fecha: date, hora_inicio: time, hora_fin: time) -> bool:
        """Consulta la disponibilidad de una sala en un horario específico - RF8"""
        # Validar sala
        sala = self.sala_repo.obtener_por_id(sala_id)
        if not sala or sala.estado != 'disponible':
            return False

        # Validar fecha
        if fecha < date.today():
            return False

        # Verificar conflictos de horario
        return not self.reserva_repo._existe_reserva_conflicto(sala_id, fecha, hora_inicio, hora_fin)

    def obtener_horarios_disponibles(self, sala_id: int, fecha: date) -> List[dict]:
        """Obtiene los horarios disponibles para una sala en una fecha específica"""
        if fecha < date.today():
            return []

        # Obtener reservas existentes para esa sala y fecha
        reservas = self.reserva_repo.obtener_activas_por_sala_y_fecha(sala_id, fecha)

        # Generar horarios disponibles (de 8:00 a 20:00 en intervalos de 30 min)
        horarios_disponibles = []
        hora_actual = time(8, 0)

        # Último inicio posible a las 19:30
        while hora_actual < time(19, 30):
            hora_fin = time(hora_actual.hour, hora_actual.minute + 30)
            if hora_fin > time(20, 0):
                break

            # Verificar si este horario está disponible
            disponible = True
            for reserva in reservas:
                if not (hora_fin <= reserva.hora_inicio or hora_actual >= reserva.hora_fin):
                    disponible = False
                    break

            if disponible:
                horarios_disponibles.append({
                    'inicio': hora_actual,
                    'fin': hora_fin,
                    'duracion': '30 min'
                })

            # Avanzar 30 minutos
            if hora_actual.minute == 30:
                hora_actual = time(hora_actual.hour + 1, 0)
            else:
                hora_actual = time(hora_actual.hour, 30)

        return horarios_disponibles

    def cancelar_reserva(self, reserva_id: int, es_administrador: bool = False) -> bool:
        """Cancela una reserva existente - RF7"""
        reserva = self.reserva_repo.obtener_por_id(reserva_id)
        if not reserva:
            raise ValueError("Reserva no encontrada")

        if reserva.estado != 'activa':
            raise ValueError("La reserva ya está cancelada o completada")

        # Aplicar políticas de cancelación
        if es_administrador:
            if not self.politica_cancelacion.puede_cancelar_administrador(reserva):
                raise ValueError("No se puede cancelar la reserva")
        else:
            if not self.politica_cancelacion.puede_cancelar_estudiante(reserva):
                raise ValueError("No se pueden cancelar reservas con menos de 1 hora de anticipación")

        # Ejecutar cancelación
        reserva.estado = 'cancelada'
        self.reserva_repo.actualizar(reserva)

        # Actualizar estado de la sala
        self._actualizar_estado_sala(reserva.sala_id)

        return True

    def modificar_reserva(self, reserva_id: int, nueva_sala_id: int = None,
                          nueva_fecha: date = None, nueva_hora_inicio: time = None,
                          nueva_hora_fin: time = None) -> bool:
        """Modifica una reserva existente - RF6"""
        reserva = self.reserva_repo.obtener_por_id(reserva_id)
        if not reserva:
            raise ValueError("Reserva no encontrada")

        if reserva.estado != 'activa':
            raise ValueError("Solo se pueden modificar reservas activas")

        # Usar valores existentes si no se proporcionan nuevos
        sala_id = nueva_sala_id if nueva_sala_id else reserva.sala_id
        fecha = nueva_fecha if nueva_fecha else reserva.fecha_reserva
        hora_inicio = nueva_hora_inicio if nueva_hora_inicio else reserva.hora_inicio
        hora_fin = nueva_hora_fin if nueva_hora_fin else reserva.hora_fin

        # Validar nueva disponibilidad (excluyendo la reserva actual)
        if self.reserva_repo._existe_reserva_conflicto(sala_id, fecha, hora_inicio, hora_fin, reserva_id):
            raise ValueError("Ya existe una reserva para la nueva sala y horario")

        # Actualizar reserva
        reserva.sala_id = sala_id
        reserva.fecha_reserva = fecha
        reserva.hora_inicio = hora_inicio
        reserva.hora_fin = hora_fin
        reserva.actualizado_en = datetime.now()

        self.reserva_repo.actualizar(reserva)

        # Actualizar estados de salas
        self._actualizar_estado_sala(reserva.sala_id)
        if nueva_sala_id and nueva_sala_id != reserva.sala_id:
            self._actualizar_estado_sala(nueva_sala_id)

        return True

    def obtener_reservas_por_estudiante(self, estudiante_id: int) -> List[Reserva]:
        """Obtiene todas las reservas de un estudiante - RF5"""
        return self.reserva_repo.obtener_por_estudiante(estudiante_id)

    def obtener_reservas_por_sala(self, sala_id: int) -> List[Reserva]:
        """Obtiene todas las reservas de una sala - RF4"""
        return self.reserva_repo.obtener_por_sala(sala_id)

    def obtener_reserva_por_id(self, reserva_id: int) -> Optional[Reserva]:
        """Obtiene una reserva específica por su ID"""
        return self.reserva_repo.obtener_por_id(reserva_id)

    def _actualizar_estado_sala(self, sala_id: int):
        """Actualiza el estado de la sala basado en reservas activas"""
        reservas_activas = self.reserva_repo.obtener_por_sala(sala_id)
        tiene_reservas_activas = any(r.estado == 'activa' for r in reservas_activas)

        nuevo_estado = 'reservada' if tiene_reservas_activas else 'disponible'
        self.sala_repo.actualizar_estado(sala_id, nuevo_estado)
