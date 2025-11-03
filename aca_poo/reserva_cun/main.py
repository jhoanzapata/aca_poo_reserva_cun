from database import DatabaseManager
from repositories import SalaRepository, ReservaRepository, EstudianteRepository
from services import ReservaService, SalaService, EstudianteService
from cli import CLIHandler
import sys
import traceback


def inicializar_servicios():
    """Inicializa y configura todos los servicios con inyección de dependencias"""
    try:
        # Configuración e inicialización de la base de datos
        db_manager = DatabaseManager()

        # Poblar datos de prueba (opcional - si el método existe)
        try:
            if hasattr(db_manager, 'poblar_datos_prueba'):
                db_manager.poblar_datos_prueba()
            else:
                print("⚠️  Método de datos de prueba no disponible")
        except Exception as e:
            print(f"⚠️  No se pudieron cargar datos de prueba: {e}")

        # Inicializar repositorios
        sala_repo = SalaRepository(db_manager)
        reserva_repo = ReservaRepository(db_manager)
        estudiante_repo = EstudianteRepository(db_manager)

        # Inicializar servicios con dependencias inyectadas
        reserva_service = ReservaService(reserva_repo, sala_repo, estudiante_repo)
        sala_service = SalaService(sala_repo)
        estudiante_service = EstudianteService(estudiante_repo)

        # Inicializar CLI con servicios
        cli = CLIHandler(reserva_service, estudiante_service, sala_service)

        return cli

    except Exception as e:
        print(f"❌ Error crítico durante la inicialización: {e}")
        print("Detalles técnicos:")
        traceback.print_exc()
        sys.exit(1)


def main():
    """Función principal de la aplicación"""
    print("🚀 Iniciando Sistema de Gestión de Reservas...")

    cli = inicializar_servicios()

    # Bucle principal de la aplicación
    while True:
        try:
            cli.mostrar_menu_principal()
            opcion = cli.pedir_opcion(1, 3)

            if opcion == 1:
                cli.manejar_menu_administrador()
            elif opcion == 2:
                cli.manejar_menu_estudiante()
            elif opcion == 3:
                print("\n🎓 ¡Gracias por usar el Sistema de Gestión de Reservas de la Universidad CUN!")
                break

        except KeyboardInterrupt:
            print("\n\n⚠️  Operación cancelada por el usuario.")
            continuar = input("¿Desea salir del sistema? (s/n): ").lower().strip()
            if continuar in ['s', 'si', 'sí', 'y', 'yes']:
                print("👋 ¡Hasta pronto!")
                break
            else:
                print("Continuando con la aplicación...")

        except Exception as e:
            print(f"\n💥 Error inesperado: {e}")
            print("El sistema se recuperará y continuará...")


if __name__ == "__main__":
    main()