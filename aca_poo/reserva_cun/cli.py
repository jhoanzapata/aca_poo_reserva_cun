import sys
from datetime import date, time, datetime
from typing import Optional, List
from models import EstadoSala, EstadoReserva


class CLIHandler:
    def __init__(self, reserva_service, estudiante_service, sala_service):
        self.reserva_service = reserva_service
        self.estudiante_service = estudiante_service
        self.sala_service = sala_service
        self.estudiante_actual = None

    def mostrar_menu_principal(self):
        """Muestra el menú principal de la aplicación"""
        print("\n" + "=" * 60)
        print("🎓 SISTEMA DE GESTIÓN DE RESERVAS - UNIVERSIDAD CUN")
        print("=" * 60)
        print("1. 👨‍💼 Menú Administrador")
        print("2. 👨‍🎓 Menú Estudiante")
        print("3. 🚪 Salir")
        print("=" * 60)

    def mostrar_menu_administrador(self):
        """Muestra el menú específico para administradores"""
        print("\n" + "=" * 50)
        print("👨‍💼 MENÚ ADMINISTRADOR")
        print("=" * 50)
        print("1. ➕ Crear Sala")
        print("2. 📋 Listar Salas")
        print("3. ✏️  Editar Sala")
        print("4. 🗑️  Eliminar Sala")
        print("5. 🔍 Consultar Reservas por Sala")
        print("6. 📊 Ver Estado de Salas")
        print("7. ❌ Cancelar Reserva")
        print("8. ↩️  Volver al Menú Principal")
        print("=" * 50)

    def mostrar_menu_estudiante(self):
        """Muestra el menú específico para estudiantes"""
        print("\n" + "=" * 50)
        print("👨‍🎓 MENÚ ESTUDIANTE")
        print("=" * 50)
        print("1. 📝 Registrarse como Estudiante")
        print("2. 🗓️  Hacer Reserva")
        print("3. 📋 Consultar Mis Reservas")
        print("4. ❌ Cancelar Mi Reserva")
        print("5. 🔍 Consultar Disponibilidad")
        print("6. ↩️  Volver al Menú Principal")
        print("=" * 50)

    def manejar_menu_administrador(self):
        """Maneja las opciones del menú administrador"""
        while True:
            self.mostrar_menu_administrador()
            opcion = self.pedir_opcion(1, 8)  # Actualizado a 8 opciones

            if opcion == 1:
                self.crear_sala()
            elif opcion == 2:
                self.listar_salas()
            elif opcion == 3:
                self.editar_sala()
            elif opcion == 4:
                self.eliminar_sala()
            elif opcion == 5:
                self.consultar_reservas_por_sala()
            elif opcion == 6:
                self.ver_estado_salas()
            elif opcion == 7:
                self.cancelar_reserva_administrador()
            elif opcion == 8:
                break

    def manejar_menu_estudiante(self):
        """Maneja las opciones del menú estudiante"""
        while True:
            self.mostrar_menu_estudiante()
            opcion = self.pedir_opcion(1, 6)

            if opcion == 1:
                self.registrar_estudiante()
            elif opcion == 2:
                self.hacer_reserva()
            elif opcion == 3:
                self.consultar_mis_reservas()
            elif opcion == 4:
                self.cancelar_mi_reserva()
            elif opcion == 5:
                self.consultar_disponibilidad()
            elif opcion == 6:
                break

    # ========== MÉTODOS DE ADMINISTRADOR ==========

    def listar_salas(self):
        """Lista todas las salas disponibles"""
        try:
            print("\n--- LISTA DE SALAS ---")
            salas = self.sala_service.listar_salas()

            if not salas:
                print("No hay salas registradas.")
                return

            for sala in salas:
                estado_icon = "🟢" if sala.estado == EstadoSala.DISPONIBLE else "🔴" if sala.estado == EstadoSala.RESERVADA else "🟡"
                print(
                    f"{estado_icon} ID: {sala.id} | {sala.nombre} | Capacidad: {sala.capacidad} | Estado: {sala.estado.value}")
                if sala.descripcion:
                    print(f"   Descripción: {sala.descripcion}")
                print()

        except Exception as e:
            self.mostrar_error(f"Error al listar salas: {e}")
        finally:
            self.pausar()

    def consultar_reservas_por_sala(self):
        """Consulta las reservas de una sala específica"""
        try:
            print("\n--- RESERVAS POR SALA ---")

            salas = self.sala_service.listar_salas()
            if not salas:
                print("No hay salas registradas.")
                return

            print("Salas disponibles:")
            for sala in salas:
                print(f"ID: {sala.id} | {sala.nombre}")

            sala_id = int(input("\nID de la sala: "))
            reservas = self.reserva_service.obtener_reservas_por_sala(sala_id)

            if not reservas:
                print("No hay reservas para esta sala.")
                return

            print(f"\nReservas para la sala:")
            for reserva in reservas:
                estado_icon = "🟢" if reserva.estado == EstadoReserva.ACTIVA else "🔴"
                print(f"{estado_icon} Reserva ID: {reserva.id}")
                print(f"   Estudiante: {getattr(reserva, 'estudiante_nombre', 'N/A')}")
                print(f"   Fecha: {reserva.fecha_reserva}")
                print(f"   Hora: {reserva.hora_inicio} - {reserva.hora_fin}")
                print(f"   Estado: {reserva.estado.value}")
                print()

        except ValueError:
            self.mostrar_error("ID de sala debe ser un número")
        except Exception as e:
            self.mostrar_error(f"Error al consultar reservas: {e}")
        finally:
            self.pausar()

    def ver_estado_salas(self):
        """Muestra el estado actual de todas las salas"""
        try:
            print("\n--- ESTADO DE SALAS ---")
            estado_salas = self.sala_service.obtener_estado_salas()

            if not estado_salas:
                print("No hay salas registradas.")
                self.pausar()
                return

            for estado in estado_salas:
                sala = estado['sala']
                estado_icon = "🟢" if sala.estado == EstadoSala.DISPONIBLE else "🔴" if sala.estado == EstadoSala.RESERVADA else "🟡"
                print(f"{estado_icon} {sala.nombre}")
                print(f"   Estado: {sala.estado.value}")
                print(f"   Capacidad: {sala.capacidad}")
                if sala.descripcion:
                    print(f"   Descripción: {sala.descripcion}")
                print()

        except Exception as e:
            self.mostrar_error(f"Error al consultar estado: {e}")
        finally:
            self.pausar()

    def cancelar_reserva_administrador(self):
        """Cancela una reserva (admin)"""
        try:
            print("\n--- CANCELAR RESERVA (ADMIN) ---")
            reserva_id = int(input("ID de la reserva a cancelar: "))

            # Mostrar información de la reserva antes de cancelar
            reserva = self.reserva_service.obtener_reserva_por_id(reserva_id)
            if not reserva:
                self.mostrar_error("Reserva no encontrada")
                return

            print(f"\n📋 Información de la reserva:")
            print(f"   ID: {reserva.id}")
            print(f"   Estudiante ID: {reserva.estudiante_id}")
            print(f"   Sala ID: {reserva.sala_id}")
            print(f"   Fecha: {reserva.fecha_reserva}")
            print(f"   Horario: {reserva.hora_inicio} - {reserva.hora_fin}")

            confirmar = input("\n¿Está seguro de cancelar esta reserva? (s/n): ").lower().strip()
            if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                self.mostrar_exito("Cancelación cancelada")
                return

            self.reserva_service.cancelar_reserva(reserva_id, es_administrador=True)
            self.mostrar_exito("Reserva cancelada exitosamente")

        except ValueError as e:
            self.mostrar_error(f"Datos inválidos: {e}")
        except Exception as e:
            self.mostrar_error(f"Error al cancelar reserva: {e}")
        finally:
            self.pausar()

    # ========== MÉTODOS DE ESTUDIANTE ==========

    def registrar_estudiante(self):
        """Registra un nuevo estudiante"""
        try:
            print("\n--- REGISTRO DE ESTUDIANTE ---")
            identificacion = input("Número de identificación: ").strip()
            nombre = input("Nombre completo: ").strip()
            email = input("Email (opcional): ").strip() or None

            # Verificar si el estudiante ya existe
            estudiante_existente = self.estudiante_service.obtener_estudiante_por_identificacion(identificacion)
            if estudiante_existente:
                self.mostrar_exito(f"Estudiante ya registrado. Bienvenido de nuevo, {estudiante_existente.nombre}!")
                self.estudiante_actual = estudiante_existente.id
                return

            estudiante_id = self.estudiante_service.registrar_estudiante(identificacion, nombre, email)
            self.estudiante_actual = estudiante_id
            self.mostrar_exito(f"Estudiante '{nombre}' registrado exitosamente (ID: {estudiante_id})")

        except ValueError as e:
            self.mostrar_error(f"Datos inválidos: {e}")
        except Exception as e:
            self.mostrar_error(f"Error al registrar estudiante: {e}")
        finally:
            self.pausar()

    def hacer_reserva(self):
        """Realiza una nueva reserva"""
        try:
            if not self.estudiante_actual:
                self.mostrar_error("Debe registrarse como estudiante primero")
                return

            print("\n--- NUEVA RESERVA ---")

            # Listar salas disponibles
            salas = self.sala_service.listar_salas_disponibles()
            if not salas:
                self.mostrar_error("No hay salas disponibles en este momento")
                return

            print("Salas disponibles:")
            for sala in salas:
                print(f"ID: {sala.id} | {sala.nombre} | Capacidad: {sala.capacidad}")

            sala_id = int(input("\nID de la sala: "))

            # Verificar que la sala existe y está disponible
            sala = self.sala_service.obtener_sala_por_id(sala_id)
            if not sala or not sala.puede_ser_reservada():
                self.mostrar_error("Sala no encontrada o no disponible")
                return

            fecha = self.pedir_fecha("Fecha de reserva (YYYY-MM-DD): ")

            # Validar fecha
            if fecha < date.today():
                self.mostrar_error("No se pueden hacer reservas en fechas pasadas")
                return

            print("\nHorario de reserva:")
            hora_inicio = self.pedir_hora("Hora de inicio (HH:MM): ")
            hora_fin = self.pedir_hora("Hora de fin (HH:MM): ")

            # Validar horario
            horario_errores = self.validar_horario_reserva(hora_inicio, hora_fin)
            if horario_errores:
                for error in horario_errores:
                    self.mostrar_error(error)
                return

            # Validar disponibilidad
            if not self.reserva_service.consultar_disponibilidad(sala_id, fecha, hora_inicio, hora_fin):
                self.mostrar_error("La sala no está disponible en ese horario")
                return

            # Confirmación
            print(f"\n📋 Resumen de la reserva:")
            print(f"   Sala: {sala.nombre}")
            print(f"   Fecha: {fecha}")
            print(f"   Horario: {hora_inicio} - {hora_fin}")

            confirmar = input("\n¿Confirmar la reserva? (s/n): ").lower().strip()
            if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                self.mostrar_exito("Reserva cancelada")
                return

            reserva_id = self.reserva_service.crear_reserva(
                self.estudiante_actual, sala_id, fecha, hora_inicio, hora_fin
            )

            self.mostrar_exito(f"Reserva creada exitosamente (ID: {reserva_id})")

        except ValueError as e:
            self.mostrar_error(f"Datos inválidos: {e}")
        except Exception as e:
            self.mostrar_error(f"Error al crear reserva: {e}")
        finally:
            self.pausar()

    def consultar_mis_reservas(self):
        """Consulta las reservas del estudiante actual"""
        try:
            if not self.estudiante_actual:
                self.mostrar_error("Debe registrarse como estudiante primero")
                return

            print("\n--- MIS RESERVAS ---")
            reservas = self.reserva_service.obtener_reservas_por_estudiante(self.estudiante_actual)

            if not reservas:
                print("No tiene reservas activas.")
                return

            for reserva in reservas:
                estado_icon = "🟢" if reserva.estado == EstadoReserva.ACTIVA else "🔴"
                print(f"{estado_icon} Reserva ID: {reserva.id}")

                # Obtener nombre de la sala
                sala_nombre = "N/A"
                try:
                    sala = self.sala_service.obtener_sala_por_id(reserva.sala_id)
                    if sala:
                        sala_nombre = sala.nombre
                except:
                    if hasattr(reserva, 'sala_nombre') and reserva.sala_nombre:
                        sala_nombre = reserva.sala_nombre

                print(f"   Sala: {sala_nombre}")
                print(f"   Fecha: {reserva.fecha_reserva}")
                print(f"   Hora: {reserva.hora_inicio} - {reserva.hora_fin}")
                print(f"   Estado: {reserva.estado.value}")
                print()

        except Exception as e:
            self.mostrar_error(f"Error al consultar reservas: {e}")
        finally:
            self.pausar()

    def cancelar_mi_reserva(self):
        """Cancela una reserva del estudiante actual"""
        try:
            if not self.estudiante_actual:
                self.mostrar_error("Debe registrarse como estudiante primero")
                return

            print("\n--- CANCELAR MI RESERVA ---")
            reserva_id = int(input("ID de la reserva a cancelar: "))

            # Obtener la reserva específica
            reservas = self.reserva_service.obtener_reservas_por_estudiante(self.estudiante_actual)
            reserva_a_cancelar = None

            for reserva in reservas:
                if reserva.id == reserva_id:
                    reserva_a_cancelar = reserva
                    break

            if not reserva_a_cancelar:
                self.mostrar_error("Reserva no encontrada o no le pertenece")
                return

            # Mostrar información
            sala_nombre = "N/A"
            try:
                sala = self.sala_service.obtener_sala_por_id(reserva_a_cancelar.sala_id)
                if sala:
                    sala_nombre = sala.nombre
            except:
                pass

            print(f"\n📋 Información de la reserva:")
            print(f"   Sala: {sala_nombre}")
            print(f"   Fecha: {reserva_a_cancelar.fecha_reserva}")
            print(f"   Horario: {reserva_a_cancelar.hora_inicio} - {reserva_a_cancelar.hora_fin}")

            confirmar = input("\n¿Está seguro de que desea cancelar esta reserva? (s/n): ").lower().strip()
            if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                self.mostrar_exito("Cancelación cancelada")
                return

            self.reserva_service.cancelar_reserva(reserva_id)
            self.mostrar_exito("Reserva cancelada exitosamente")

        except ValueError as e:
            self.mostrar_error(f"ID inválido: {e}")
        except Exception as e:
            self.mostrar_error(f"Error al cancelar reserva: {e}")
        finally:
            self.pausar()

    def consultar_disponibilidad(self):
        """Consulta disponibilidad de una sala"""
        try:
            print("\n--- CONSULTAR DISPONIBILIDAD ---")

            salas = self.sala_service.listar_salas()
            if not salas:
                print("No hay salas registradas.")
                self.pausar()
                return

            print("Salas disponibles:")
            for sala in salas:
                print(f"ID: {sala.id} | {sala.nombre}")

            sala_id = int(input("\nID de la sala: "))
            fecha = self.pedir_fecha("Fecha a consultar (YYYY-MM-DD): ")
            hora_inicio = self.pedir_hora("Hora de inicio (HH:MM): ")
            hora_fin = self.pedir_hora("Hora de fin (HH:MM): ")

            # Validar horario
            horario_errores = self.validar_horario_reserva(hora_inicio, hora_fin)
            if horario_errores:
                for error in horario_errores:
                    self.mostrar_error(error)
                return

            disponible = self.reserva_service.consultar_disponibilidad(sala_id, fecha, hora_inicio, hora_fin)

            if disponible:
                self.mostrar_exito("La sala está disponible en ese horario")
            else:
                self.mostrar_error("La sala NO está disponible en ese horario")

        except ValueError as e:
            self.mostrar_error(f"Datos inválidos: {e}")
        except Exception as e:
            self.mostrar_error(f"Error al consultar disponibilidad: {e}")
        finally:
            self.pausar()

    # ========== MÉTODOS AUXILIARES ==========

    def pedir_opcion(self, min_opcion: int, max_opcion: int) -> int:
        """Solicita una opción válida al usuario"""
        while True:
            try:
                opcion_input = input("Seleccione una opción: ").strip()
                if not opcion_input:
                    print("❌ Entrada vacía. Por favor ingrese un número.")
                    continue

                opcion = int(opcion_input)
                if min_opcion <= opcion <= max_opcion:
                    return opcion
                else:
                    print(f"❌ Por favor, ingrese un número entre {min_opcion} y {max_opcion}")
            except ValueError:
                print("❌ Entrada inválida. Por favor ingrese un número.")

    def pedir_fecha(self, mensaje: str = "Ingrese la fecha (YYYY-MM-DD): ") -> date:
        """Solicita una fecha válida al usuario"""
        while True:
            try:
                fecha_str = input(mensaje)
                return date.fromisoformat(fecha_str)
            except ValueError:
                print("Formato de fecha inválido. Use YYYY-MM-DD")

    def pedir_hora(self, mensaje: str = "Ingrese la hora (HH:MM): ") -> time:
        """Solicita una hora válida al usuario"""
        while True:
            try:
                hora_str = input(mensaje).strip()

                # Permitir formato HHMM (sin dos puntos)
                if len(hora_str) == 4 and hora_str.isdigit():
                    hora_str = f"{hora_str[:2]}:{hora_str[2:4]}"

                # Validar formato
                if len(hora_str) != 5 or hora_str[2] != ':':
                    raise ValueError("Formato incorrecto")

                horas, minutos = map(int, hora_str.split(':'))

                if not (0 <= horas <= 23 and 0 <= minutos <= 59):
                    raise ValueError("Hora fuera de rango")

                return time(horas, minutos)

            except ValueError as e:
                print("Formato de hora inválido. Use HH:MM o HHMM (ej: 14:30 o 1430)")

    def validar_horario_reserva(self, hora_inicio: time, hora_fin: time) -> List[str]:
        """Valida que el horario de reserva sea lógico - VERSIÓN MEJORADA"""
        errores = []

        # Validación CRÍTICA: hora inicio antes de hora fin
        if hora_inicio >= hora_fin:
            errores.append("❌ La hora de inicio debe ser ANTERIOR a la hora de fin")
            return errores  # Si esta falla, las demás no tienen sentido

        # Calcular duración exacta
        duracion_minutos = (hora_fin.hour - hora_inicio.hour) * 60 + (hora_fin.minute - hora_inicio.minute)

        # Validar rango horario (8:00 - 20:00)
        if hora_inicio < time(8, 0):
            errores.append("🚫 El horario de apertura es a las 8:00 AM")

        if hora_fin > time(20, 0):
            errores.append("🚫 El horario de cierre es a las 8:00 PM")

        # Validar duración mínima (30 minutos)
        if duracion_minutos < 30:
            errores.append("⏱️  La reserva debe tener al menos 30 minutos de duración")

        # Validar duración máxima (4 horas)
        if duracion_minutos > 240:
            errores.append("⏰ La reserva no puede exceder 4 horas de duración")

        return errores

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error estandarizado"""
        print(f"\n❌ ERROR: {mensaje}")

    def mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito estandarizado"""
        print(f"\n✅ {mensaje}")

    def pausar(self):
        """Pausa la ejecución hasta que el usuario presione Enter"""
        input("\n⏎ Presione Enter para continuar...")

    def mostrar_horarios_disponibles(self, sala_id: int, fecha: date):
        """Muestra los horarios disponibles para una sala en una fecha específica"""
        try:
            horarios = self.reserva_service.obtener_horarios_disponibles(sala_id, fecha)

            if not horarios:
                print("❌ No hay horarios disponibles para esta fecha")
                return False

            print(f"\n🕐 Horarios disponibles para el {fecha}:")
            for i, horario in enumerate(horarios, 1):
                print(f"   {i}. {horario['inicio']} - {horario['fin']} ({horario['duracion']})")

            return True

        except Exception as e:
            self.mostrar_error(f"Error al obtener horarios: {e}")
            return False

    # cli.py - AGREGAR ESTOS MÉTODOS EN LA CLASE CLIHandler

    def crear_sala(self):
        """Crea una nueva sala - VERSIÓN MEJORADA"""
        try:
            print("\n--- CREAR NUEVA SALA ---")

            # Validar nombre
            nombre = input("Nombre de la sala: ").strip()
            if not nombre:
                self.mostrar_error("El nombre de la sala es obligatorio")
                return

            # Validar capacidad con manejo de errores robusto
            while True:
                capacidad_str = input("Capacidad: ").strip()
                if not capacidad_str:
                    self.mostrar_error("La capacidad es obligatoria")
                    continue

                try:
                    capacidad = int(capacidad_str)
                    if capacidad <= 0:
                        self.mostrar_error("La capacidad debe ser mayor a 0")
                        continue
                    break  # Salir del loop si todo está bien
                except ValueError:
                    self.mostrar_error("La capacidad debe ser un número entero válido")

            descripcion = input("Descripción (opcional): ").strip() or None

            # Crear sala usando el servicio (SOLO lógica de negocio)
            sala_id = self.sala_service.crear_sala(nombre, capacidad, descripcion)
            self.mostrar_exito(f"Sala '{nombre}' creada exitosamente (ID: {sala_id})")

        except Exception as e:
            self.mostrar_error(f"Error al crear sala: {e}")
        finally:
            self.pausar()

    def editar_sala(self):
        """Edita una sala existente"""
        try:
            print("\n--- EDITAR SALA ---")

            # Listar salas para que el usuario vea las opciones
            salas = self.sala_service.listar_salas()
            if not salas:
                self.mostrar_error("No hay salas para editar")
                return

            for sala in salas:
                estado_icon = "🟢" if sala.estado == EstadoSala.DISPONIBLE else "🔴" if sala.estado == EstadoSala.RESERVADA else "🟡"
                print(f"{estado_icon} ID: {sala.id} | {sala.nombre}")

            sala_id = int(input("\nID de la sala a editar: "))

            # Obtener sala actual
            sala_actual = self.sala_service.obtener_sala_por_id(sala_id)
            if not sala_actual:
                self.mostrar_error("Sala no encontrada")
                return

            print(f"\nEditando: {sala_actual.nombre}")
            print("(Deje en blanco para mantener el valor actual)")

            # Solicitar nuevos datos
            nuevo_nombre = input(f"Nuevo nombre [{sala_actual.nombre}]: ").strip()
            nuevo_nombre = nuevo_nombre if nuevo_nombre else sala_actual.nombre

            # Manejar capacidad con validación
            while True:
                nueva_capacidad_str = input(f"Nueva capacidad [{sala_actual.capacidad}]: ").strip()
                if not nueva_capacidad_str:
                    nueva_capacidad = sala_actual.capacidad
                    break
                try:
                    nueva_capacidad = int(nueva_capacidad_str)
                    if nueva_capacidad <= 0:
                        self.mostrar_error("La capacidad debe ser mayor a 0")
                        continue
                    break
                except ValueError:
                    self.mostrar_error("La capacidad debe ser un número válido")

            nueva_descripcion = input(f"Nueva descripción [{sala_actual.descripcion or 'Sin descripción'}]: ").strip()
            nueva_descripcion = nueva_descripcion if nueva_descripcion else sala_actual.descripcion

            # Mostrar estados disponibles
            print("\nEstados disponibles: disponible, reservada, mantenimiento")
            nuevo_estado = input(f"Nuevo estado [{sala_actual.estado.value}]: ").strip()
            nuevo_estado = nuevo_estado if nuevo_estado else sala_actual.estado.value

            # Validar estado
            if nuevo_estado not in ['disponible', 'reservada', 'mantenimiento']:
                self.mostrar_error("Estado inválido. Use: disponible, reservada o mantenimiento")
                return

            # Confirmar cambios
            print(f"\n¿Confirmar cambios?")
            print(f"Nombre: {sala_actual.nombre} → {nuevo_nombre}")
            print(f"Capacidad: {sala_actual.capacidad} → {nueva_capacidad}")
            print(f"Estado: {sala_actual.estado.value} → {nuevo_estado}")

            confirmar = input("\n¿Continuar? (s/n): ").lower().strip()
            if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                self.mostrar_exito("Edición cancelada")
                return

            # Ejecutar actualización usando el servicio
            self.sala_service.actualizar_sala(sala_id, nuevo_nombre, nueva_capacidad, nueva_descripcion, nuevo_estado)
            self.mostrar_exito("Sala actualizada exitosamente")

        except ValueError as e:
            self.mostrar_error(f"Datos inválidos: {e}")
        except Exception as e:
            self.mostrar_error(f"Error al editar sala: {e}")
        finally:
            self.pausar()

    def eliminar_sala(self):
        """Elimina una sala existente"""
        try:
            print("\n--- ELIMINAR SALA ---")

            # Listar salas
            salas = self.sala_service.listar_salas()
            if not salas:
                self.mostrar_error("No hay salas para eliminar")
                return

            for sala in salas:
                estado_icon = "🟢" if sala.estado == EstadoSala.DISPONIBLE else "🔴" if sala.estado == EstadoSala.RESERVADA else "🟡"
                print(f"{estado_icon} ID: {sala.id} | {sala.nombre}")

            sala_id = int(input("\nID de la sala a eliminar: "))

            # Obtener sala para confirmación
            sala = self.sala_service.obtener_sala_por_id(sala_id)
            if not sala:
                self.mostrar_error("Sala no encontrada")
                return

            # Mostrar información de la sala
            print(f"\n⚠️  INFORMACIÓN DE LA SALA A ELIMINAR:")
            print(f"   Nombre: {sala.nombre}")
            print(f"   Capacidad: {sala.capacidad}")
            print(f"   Estado: {sala.estado.value}")
            if sala.descripcion:
                print(f"   Descripción: {sala.descripcion}")

            # Confirmación crítica
            confirmar = input("\n❌ ¿ESTÁ SEGURO de que desea ELIMINAR esta sala? (s/n): ").lower().strip()
            if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                self.mostrar_exito("Eliminación cancelada")
                return

            # Ejecutar eliminación usando el servicio
            self.sala_service.eliminar_sala(sala_id)
            self.mostrar_exito("Sala eliminada exitosamente")

        except ValueError as e:
            self.mostrar_error(f"ID inválido: {e}")
        except Exception as e:
            self.mostrar_error(f"Error al eliminar sala: {e}")
        finally:
            self.pausar()
