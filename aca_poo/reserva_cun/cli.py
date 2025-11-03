import sys
from datetime import date, time, datetime
from typing import Optional, List


class CLIHandler:
    def __init__(self, reserva_service, estudiante_service, sala_service):
        self.reserva_service = reserva_service
        self.estudiante_service = estudiante_service
        self.sala_service = sala_service
        self.estudiante_actual = None

    def mostrar_menu_principal(self):
        """Muestra el menú principal de la aplicación"""
        print("\n" + "=" * 50)
        print("SISTEMA DE GESTIÓN DE RESERVAS - UNIVERSIDAD CUN")
        print("=" * 50)
        print("1. Menú Administrador")
        print("2. Menú Estudiante")
        print("3. Salir")
        print("=" * 50)

    def mostrar_menu_administrador(self):
        """Muestra el menú específico para administradores"""
        print("\n" + "=" * 50)
        print("MENÚ ADMINISTRADOR")
        print("=" * 50)
        print("1. Crear Sala")
        print("2. Listar Salas")
        print("3. Consultar Reservas por Sala")
        print("4. Ver Estado de Salas")
        print("5. Cancelar Reserva")
        print("6. Volver al Menú Principal")
        print("=" * 50)

    def mostrar_menu_estudiante(self):
        """Muestra el menú específico para estudiantes"""
        print("\n" + "=" * 50)
        print("MENÚ ESTUDIANTE")
        print("=" * 50)
        print("1. Registrarse como Estudiante")
        print("2. Hacer Reserva")
        print("3. Consultar Mis Reservas")
        print("4. Cancelar Mi Reserva")
        print("5. Consultar Disponibilidad")
        print("6. Volver al Menú Principal")
        print("=" * 50)

    def manejar_menu_administrador(self):
        """Maneja las opciones del menú administrador"""
        while True:
            self.mostrar_menu_administrador()
            opcion = self.pedir_opcion(1, 6)

            if opcion == 1:
                self.crear_sala()
            elif opcion == 2:
                self.listar_salas()
            elif opcion == 3:
                self.consultar_reservas_por_sala()
            elif opcion == 4:
                self.ver_estado_salas()
            elif opcion == 5:
                self.cancelar_reserva_administrador()
            elif opcion == 6:
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

    def crear_sala(self):
        """Crea una nueva sala"""
        try:
            print("\n--- CREAR NUEVA SALA ---")
            nombre = input("Nombre de la sala: ").strip()
            capacidad = int(input("Capacidad: "))
            descripcion = input("Descripción (opcional): ").strip() or None

            sala_id = self.sala_service.crear_sala(nombre, capacidad, descripcion)
            self.mostrar_exito(f"Sala '{nombre}' creada exitosamente (ID: {sala_id})")

        except ValueError as e:
            self.mostrar_error(f"Datos inválidos: {e}")
        except Exception as e:
            self.mostrar_error(f"Error al crear sala: {e}")
        finally:
            self.pausar()

    def listar_salas(self):
        """Lista todas las salas disponibles - versión corregida"""
        try:
            print("\n--- LISTA DE SALAS ---")
            salas = self.sala_service.listar_salas()

            if not salas:
                print("No hay salas registradas.")
                return  # Remover pausar() de aquí

            for sala in salas:
                estado_icon = "🟢" if sala.estado == 'disponible' else "🔴" if sala.estado == 'reservada' else "🟡"
                print(
                    f"{estado_icon} ID: {sala.id} | {sala.nombre} | Capacidad: {sala.capacidad} | Estado: {sala.estado}")
                if sala.descripcion:
                    print(f"   Descripción: {sala.descripcion}")
                print()

        except Exception as e:
            self.mostrar_error(f"Error al listar salas: {e}")
        finally:
            self.pausar()  # Solo un pausar() aquí

    def registrar_estudiante(self):
        """Registra un nuevo estudiante - versión mejorada"""
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
        """Realiza una nueva reserva - VERSIÓN CORREGIDA"""
        try:
            if not self.estudiante_actual:
                self.mostrar_error("Debe registrarse como estudiante primero")
                return

            print("\n--- NUEVA RESERVA ---")

            # Listar salas disponibles
            salas = self.sala_service.listar_salas()
            salas_disponibles = [s for s in salas if s.estado == 'disponible']

            if not salas_disponibles:
                self.mostrar_error("No hay salas disponibles en este momento")
                return

            print("Salas disponibles:")
            for sala in salas_disponibles:
                print(f"ID: {sala.id} | {sala.nombre} | Capacidad: {sala.capacidad}")

            sala_id = int(input("\nID de la sala: "))

            # ✅ CORREGIDO: Verificar que la sala existe y está disponible
            sala_encontrada = None
            for sala in salas_disponibles:
                if sala.id == sala_id:
                    sala_encontrada = sala
                    break

            if not sala_encontrada:
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
            errores_horario = self.validar_horario_reserva(hora_inicio, hora_fin)
            if errores_horario:
                for error in errores_horario:
                    self.mostrar_error(error)
                return

            # Validar disponibilidad
            if not self.reserva_service.consultar_disponibilidad(sala_id, fecha, hora_inicio, hora_fin):
                self.mostrar_error("La sala no está disponible en ese horario")
                return

            # Confirmación
            print(f"\n📋 Resumen de la reserva:")
            print(f"   Sala: {sala_encontrada.nombre}")
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
        """Consulta las reservas del estudiante actual - VERSIÓN MEJORADA"""
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
                estado_icon = "🟢" if reserva.estado == 'activa' else "🔴"
                print(f"{estado_icon} Reserva ID: {reserva.id}")

                # ✅ MEJORADO: Obtener nombre de sala de forma confiable
                sala_nombre = "N/A"
                try:
                    # Intentar obtener la sala completa para tener el nombre
                    sala = self.sala_service.obtener_sala_por_id(reserva.sala_id)
                    if sala:
                        sala_nombre = sala.nombre
                except:
                    # Si falla, usar el atributo si existe
                    if hasattr(reserva, 'sala_nombre') and reserva.sala_nombre:
                        sala_nombre = reserva.sala_nombre
                    elif reserva.sala and hasattr(reserva.sala, 'nombre'):
                        sala_nombre = reserva.sala.nombre

                print(f"   Sala: {sala_nombre}")
                print(f"   Fecha: {reserva.fecha_reserva}")
                print(f"   Hora: {reserva.hora_inicio} - {reserva.hora_fin}")
                print(f"   Estado: {reserva.estado}")
                print()

        except Exception as e:
            self.mostrar_error(f"Error al consultar reservas: {e}")
        finally:
            self.pausar()

    def consultar_reservas_por_sala(self):
        """Consulta las reservas de una sala específica - versión corregida"""
        try:
            print("\n--- RESERVAS POR SALA ---")

            salas = self.sala_service.listar_salas()
            if not salas:
                print("No hay salas registradas.")
                return  # Solo return, no pausar aquí

            print("Salas disponibles:")
            for sala in salas:
                print(f"ID: {sala.id} | {sala.nombre}")

            sala_id = int(input("\nID de la sala: "))
            reservas = self.reserva_service.obtener_reservas_por_sala(sala_id)

            if not reservas:
                print("No hay reservas para esta sala.")
                return  # Solo return, no pausar aquí

            print(f"\nReservas para la sala:")
            for reserva in reservas:
                estado_icon = "🟢" if reserva.estado == 'activa' else "🔴"
                print(f"{estado_icon} Reserva ID: {reserva.id}")
                print(f"   Estudiante: {getattr(reserva, 'estudiante_nombre', 'N/A')}")
                print(f"   Fecha: {reserva.fecha_reserva}")
                print(f"   Hora: {reserva.hora_inicio} - {reserva.hora_fin}")
                print(f"   Estado: {reserva.estado}")
                print()

        except ValueError:
            self.mostrar_error("ID de sala debe ser un número")
        except Exception as e:
            self.mostrar_error(f"Error al consultar reservas: {e}")
        finally:
            self.pausar()  # Solo UNA pausa al final

    def ver_estado_salas(self):
        """Muestra el estado actual de todas las salas"""
        try:
            print("\n--- ESTADO DE SALAS ---")
            salas = self.sala_service.listar_salas()

            if not salas:
                print("No hay salas registradas.")
                self.pausar()
                return

            for sala in salas:
                # Contar reservas activas para hoy
                hoy = date.today()
                reservas_hoy = [
                    r for r in self.reserva_service.obtener_reservas_por_sala(sala.id)
                    if r.fecha_reserva == hoy and r.estado == 'activa'
                ]

                estado_icon = "🟢" if sala.estado == 'disponible' else "🔴" if sala.estado == 'reservada' else "🟡"
                print(f"{estado_icon} {sala.nombre}")
                print(f"   Estado: {sala.estado}")
                print(f"   Reservas para hoy: {len(reservas_hoy)}")
                if reservas_hoy:
                    print("   Horarios ocupados:")
                    for r in reservas_hoy:
                        print(f"     - {r.hora_inicio} a {r.hora_fin}")
                print()

        except Exception as e:
            self.mostrar_error(f"Error al consultar estado: {e}")
        finally:
            self.pausar()

    def cancelar_reserva_administrador(self):
        """Cancela una reserva (admin) - VERSIÓN MEJORADA"""
        try:
            print("\n--- CANCELAR RESERVA (ADMIN) ---")
            reserva_id = int(input("ID de la reserva a cancelar: "))

            # Obtener información de la reserva para mostrar
            reservas_todas = []
            salas = self.sala_service.listar_salas()
            for sala in salas:
                reservas_todas.extend(self.reserva_service.obtener_reservas_por_sala(sala.id))

            reserva_obj = next((r for r in reservas_todas if r.id == reserva_id), None)

            if not reserva_obj:
                self.mostrar_error("Reserva no encontrada")
                return

            # Mostrar información de la reserva
            print(f"\n📋 Información de la reserva:")
            sala_nombre = getattr(reserva_obj, 'sala_nombre', 'N/A')
            estudiante_nombre = getattr(reserva_obj, 'estudiante_nombre', 'N/A')
            print(f"   Estudiante: {estudiante_nombre}")
            print(f"   Sala: {sala_nombre}")
            print(f"   Fecha: {reserva_obj.fecha_reserva}")
            print(f"   Horario: {reserva_obj.hora_inicio} - {reserva_obj.hora_fin}")

            confirmar = input("\n¿Está seguro de cancelar esta reserva? (s/n): ").lower().strip()
            if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                self.mostrar_exito("Cancelación cancelada")
                return

            self.reserva_service.cancelar_reserva(reserva_id, es_administrador=True)
            self.mostrar_exito("Reserva cancelada exitosamente")

        except ValueError as e:
            error_msg = str(e)
            if "Reserva no encontrada" in error_msg:
                self.mostrar_error("Reserva no encontrada")
            elif "No se pueden cancelar reservas pasadas" in error_msg:
                self.mostrar_error("No se pueden cancelar reservas pasadas")
            else:
                self.mostrar_error(f"Datos inválidos: {e}")
        except Exception as e:
            self.mostrar_error(f"Error al cancelar reserva: {e}")
        finally:
            self.pausar()

    def cancelar_mi_reserva(self):
        """Cancela una reserva del estudiante actual - VERSIÓN CORREGIDA"""
        try:
            if not self.estudiante_actual:
                self.mostrar_error("Debe registrarse como estudiante primero")
                return

            print("\n--- CANCELAR MI RESERVA ---")
            reserva_id = int(input("ID de la reserva a cancelar: "))

            # Obtener todas las reservas del estudiante
            reservas = self.reserva_service.obtener_reservas_por_estudiante(self.estudiante_actual)

            # Buscar la reserva específica
            reserva_a_cancelar = None
            for reserva in reservas:
                if reserva.id == reserva_id:
                    reserva_a_cancelar = reserva
                    break

            if not reserva_a_cancelar:
                self.mostrar_error("Reserva no encontrada o no le pertenece")
                return

            # ✅ CORREGIDO: Obtener nombre real de la sala
            sala_nombre = "N/A"
            try:
                sala = self.sala_service.obtener_sala_por_id(reserva_a_cancelar.sala_id)
                if sala:
                    sala_nombre = sala.nombre
            except:
                # Si falla, intentar obtener de los atributos de la reserva
                if hasattr(reserva_a_cancelar, 'sala_nombre') and reserva_a_cancelar.sala_nombre:
                    sala_nombre = reserva_a_cancelar.sala_nombre

            # Mostrar información
            print(f"\n📋 Información de la reserva:")
            print(f"   Sala: {sala_nombre}")
            print(f"   Fecha: {reserva_a_cancelar.fecha_reserva}")
            print(f"   Horario: {reserva_a_cancelar.hora_inicio} - {reserva_a_cancelar.hora_fin}")
            print(f"   Estado actual: {reserva_a_cancelar.estado}")

            confirmar = input("\n¿Está seguro de que desea cancelar esta reserva? (s/n): ").lower().strip()
            if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                self.mostrar_exito("Cancelación cancelada")
                return

            # ✅ CORREGIDO: Llamar al servicio de cancelación
            self.reserva_service.cancelar_reserva(reserva_id)
            self.mostrar_exito("Reserva cancelada exitosamente")

        except ValueError as e:
            self.mostrar_error(f"ID inválido: {e}")
        except Exception as e:
            error_msg = str(e)
            if "Reserva no encontrada" in error_msg:
                self.mostrar_error("Reserva no encontrada")
            elif "No se pueden cancelar reservas pasadas" in error_msg:
                self.mostrar_error("No se pueden cancelar reservas pasadas")
            elif "No se pueden cancelar reservas con menos de 1 hora de anticipación" in error_msg:
                self.mostrar_error("No se pueden cancelar reservas con menos de 1 hora de anticipación")
            else:
                self.mostrar_error(f"Error al cancelar reserva: {e}")
        finally:
            self.pausar()

    def consultar_disponibilidad(self):
        """Consulta disponibilidad de una sala - VERSIÓN TEMPORAL"""
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

            # SOLUCIÓN TEMPORAL: Buscar en la lista de salas
            sala_encontrada = None
            for sala in salas:
                if sala.id == sala_id:
                    sala_encontrada = sala
                    break

            if not sala_encontrada:
                self.mostrar_error("Sala no encontrada")
                return

            fecha = self.pedir_fecha("Fecha a consultar (YYYY-MM-DD): ")
            hora_inicio = self.pedir_hora("Hora de inicio (HH:MM): ")
            hora_fin = self.pedir_hora("Hora de fin (HH:MM): ")

            # Validar horario
            errores_horario = self.validar_horario_reserva(hora_inicio, hora_fin)
            if errores_horario:
                for error in errores_horario:
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

    def pedir_opcion(self, min_opcion: int, max_opcion: int) -> int:
        """Solicita una opción válida al usuario - VERSIÓN MEJORADA"""
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
        """Solicita una hora válida al usuario - versión mejorada"""
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
            errores.append("La hora de inicio debe ser anterior a la hora de fin")
            # Si esta validación falla, las siguientes no tienen sentido
            return errores

        # Validar rango horario (8:00 - 20:00)
        if hora_inicio < time(8, 0):
            errores.append("La hora de inicio no puede ser antes de las 8:00")

        if hora_fin > time(20, 0):
            errores.append("La hora de fin no puede ser después de las 20:00")

        # Validar duración mínima (30 minutos)
        duracion_minutos = (hora_fin.hour - hora_inicio.hour) * 60 + (hora_fin.minute - hora_inicio.minute)
        if duracion_minutos < 30:
            errores.append("La reserva debe tener al menos 30 minutos de duración")

        # Validar duración máxima (4 horas)
        if duracion_minutos > 240:
            errores.append("La reserva no puede exceder 4 horas de duración")

        return errores

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error estandarizado"""
        print(f"\n❌ ERROR: {mensaje}")

    def mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito estandarizado"""
        print(f"\n✅ {mensaje}")

    def pausar(self):
        """Pausa la ejecución hasta que el usuario presione Enter"""
        input("\nPresione Enter para continuar...")
