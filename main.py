
from abc import ABC, abstractmethod
from datetime import datetime
import logging

# =====================================================
# CONFIGURACION DEL ARCHIVO DE REGISTRO
# =====================================================

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# =====================================================
# EXCEPCIONES PERSONALIZADAS
# =====================================================

class ErrorSistema(Exception):
    """Excepcion general del sistema."""
    pass


class DatosInvalidos(ErrorSistema):
    """Se produce cuando los datos no son validos."""
    pass


class ServicioNoDisponible(ErrorSistema):
    """Se produce cuando un servicio no esta disponible."""
    pass


class ReservaInvalida(ErrorSistema):
    """Se produce cuando una reserva no puede procesarse."""
    pass


# =====================================================
# CLASE ABSTRACTA ENTIDAD
# =====================================================

class Entidad(ABC):

    def __init__(self, identificacion):
        if not identificacion:
            raise DatosInvalidos("La identificacion es obligatoria.")

        self._identificacion = identificacion

    @abstractmethod
    def mostrar_informacion(self):
        pass


# =====================================================
# CLASE CLIENTE
# =====================================================

class Cliente(Entidad):

    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(identificacion)

        if not nombre.strip():
            raise DatosInvalidos("El nombre no puede estar vacio.")

        if "@" not in correo or "." not in correo:
            raise DatosInvalidos("El correo electronico no es valido.")

        if not telefono.isdigit() or len(telefono) < 7:
            raise DatosInvalidos("El telefono no es valido.")

        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    def mostrar_informacion(self):
        return (
            f"Cliente: {self.__nombre} | "
            f"Correo: {self.__correo} | "
            f"Telefono: {self.__telefono}"
        )


# =====================================================
# CLASE ABSTRACTA SERVICIO
# =====================================================

class Servicio(ABC):

    def __init__(self, codigo, nombre, precio):
        if precio <= 0:
            raise DatosInvalidos("El precio debe ser mayor que cero.")

        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.disponible = True

    @abstractmethod
    def calcular_costo(self, cantidad=1, impuesto=0, descuento=0):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    def validar_disponibilidad(self):
        if not self.disponible:
            raise ServicioNoDisponible(
                f"El servicio {self.nombre} no esta disponible."
            )
        return True


# =====================================================
# SERVICIO 1: RESERVA DE SALAS
# =====================================================

class ReservaSala(Servicio):

    def calcular_costo(self, cantidad=1, impuesto=0, descuento=0):
        subtotal = self.precio * cantidad
        return subtotal + (subtotal * impuesto / 100) - descuento

    def describir_servicio(self):
        return f"Reserva de sala: {self.nombre}"


# =====================================================
# SERVICIO 2: ALQUILER DE EQUIPOS
# =====================================================

class AlquilerEquipo(Servicio):

    def calcular_costo(self, cantidad=1, impuesto=0, descuento=0):
        subtotal = self.precio * cantidad
        return subtotal + (subtotal * impuesto / 100) - descuento

    def describir_servicio(self):
        return f"Alquiler de equipo: {self.nombre}"


# =====================================================
# SERVICIO 3: ASESORIAS ESPECIALIZADAS
# =====================================================

class Asesoria(Servicio):

    def calcular_costo(self, cantidad=1, impuesto=0, descuento=0):
        subtotal = self.precio * cantidad
        return subtotal + (subtotal * impuesto / 100) - descuento

    def describir_servicio(self):
        return f"Asesoria especializada: {self.nombre}"


# =====================================================
# CLASE RESERVA
# =====================================================

class Reserva(Entidad):

    def __init__(self, codigo, cliente, servicio, duracion):
        super().__init__(codigo)

        if not isinstance(cliente, Cliente):
            raise DatosInvalidos("El cliente no es valido.")

        if not isinstance(servicio, Servicio):
            raise DatosInvalidos("El servicio no es valido.")

        if duracion <= 0:
            raise DatosInvalidos("La duracion debe ser mayor que cero.")

        servicio.validar_disponibilidad()

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"

    def confirmar(self):
        if self.estado != "Pendiente":
            raise ReservaInvalida(
                "Solo se pueden confirmar reservas pendientes."
            )

        self.estado = "Confirmada"
        logging.info(f"Reserva {self._identificacion} confirmada.")

    def cancelar(self):
        if self.estado == "Cancelada":
            raise ReservaInvalida("La reserva ya esta cancelada.")

        self.estado = "Cancelada"
        logging.info(f"Reserva {self._identificacion} cancelada.")

    def procesar(self):
        try:
            self.servicio.validar_disponibilidad()
            self.confirmar()

        except ErrorSistema as error:
            logging.error(f"Error al procesar reserva: {error}")
            raise ReservaInvalida(
                "No fue posible procesar la reserva."
            ) from error

        else:
            print("Reserva procesada correctamente.")

        finally:
            logging.info(
                f"Finalizo el procesamiento de reserva "
                f"{self._identificacion}."
            )

    def mostrar_informacion(self):
        return (
            f"Reserva: {self._identificacion} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Duracion: {self.duracion} | "
            f"Estado: {self.estado}"
        )


# =====================================================
# CLASE PRINCIPAL DEL SISTEMA SOFTWARE FJ
# =====================================================

class SistemaSoftwareFJ:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        try:
            if not isinstance(cliente, Cliente):
                raise DatosInvalidos("El cliente no es valido.")

            if any(c._identificacion == cliente._identificacion
                   for c in self.clientes):
                raise DatosInvalidos("El cliente ya esta registrado.")

            self.clientes.append(cliente)
            logging.info(f"Cliente registrado: {cliente.nombre}")
            print("Cliente registrado correctamente.")

        except DatosInvalidos as error:
            logging.error(f"Error registrando cliente: {error}")
            print("Error:", error)

    def agregar_servicio(self, servicio):
        try:
            if not isinstance(servicio, Servicio):
                raise DatosInvalidos("Tipo de servicio incorrecto.")

            if any(s.codigo == servicio.codigo for s in self.servicios):
                raise DatosInvalidos("El servicio ya existe.")

            self.servicios.append(servicio)
            logging.info(f"Servicio agregado: {servicio.nombre}")
            print("Servicio agregado correctamente.")

        except DatosInvalidos as error:
            logging.error(f"Error agregando servicio: {error}")
            print("Error:", error)

    def crear_reserva(self, codigo, cliente, servicio, duracion):
        try:
            reserva = Reserva(codigo, cliente, servicio, duracion)

            if any(r._identificacion == codigo for r in self.reservas):
                raise ReservaInvalida("El codigo de reserva ya existe.")

            self.reservas.append(reserva)
            logging.info(f"Reserva creada: {codigo}")
            print("Reserva creada correctamente.")
            return reserva

        except ErrorSistema as error:
            logging.error(f"Error creando reserva: {error}")
            print("Error:", error)
            return None

    def mostrar_clientes(self):
        print("\n--- CLIENTES REGISTRADOS ---")
        for cliente in self.clientes:
            print(cliente.mostrar_informacion())

    def mostrar_servicios(self):
        print("\n--- SERVICIOS DISPONIBLES ---")
        for servicio in self.servicios:
            print(servicio.describir_servicio())

    def mostrar_reservas(self):
        print("\n--- RESERVAS REGISTRADAS ---")
        for reserva in self.reservas:
            print(reserva.mostrar_informacion())


# =====================================================
# PROGRAMA PRINCIPAL Y PRUEBAS
# =====================================================

def ejecutar_sistema():

    sistema = SistemaSoftwareFJ()

    print("=" * 55)
    print("       SOFTWARE FJ - SISTEMA DE GESTION")
    print("=" * 55)

    print("\nOPERACION 1: Registrar cliente valido")
    cliente1 = Cliente(
        "1001", "Carlos Perez",
        "carlos@gmail.com", "3001234567"
    )
    sistema.registrar_cliente(cliente1)

    print("\nOPERACION 2: Registrar segundo cliente")
    cliente2 = Cliente(
        "1002", "Maria Rodriguez",
        "maria@gmail.com", "3101234567"
    )
    sistema.registrar_cliente(cliente2)

    print("\nOPERACION 3: Intentar registrar cliente invalido")
    try:
        cliente_invalido = Cliente(
            "1003", "Pedro Lopez",
            "correo_invalido", "123"
        )
        sistema.registrar_cliente(cliente_invalido)
    except DatosInvalidos as error:
        logging.error(f"Cliente invalido: {error}")
        print("Error controlado:", error)

    print("\nOPERACION 4: Crear servicio de sala")
    sala = ReservaSala("S01", "Sala de reuniones", 50000)
    sistema.agregar_servicio(sala)

    print("\nOPERACION 5: Crear servicio de alquiler")
    equipo = AlquilerEquipo("E01", "Video Beam", 30000)
    sistema.agregar_servicio(equipo)

    print("\nOPERACION 6: Crear servicio de asesoria")
    asesoria = Asesoria("A01", "Asesoria informatica", 80000)
    sistema.agregar_servicio(asesoria)

    print("\nOPERACION 7: Intentar crear servicio invalido")
    try:
        servicio_invalido = ReservaSala("S02", "Sala invalida", -100)
        sistema.agregar_servicio(servicio_invalido)
    except DatosInvalidos as error:
        logging.error(f"Servicio invalido: {error}")
        print("Error controlado:", error)

    print("\nOPERACION 8: Crear reserva de sala")
    reserva1 = sistema.crear_reserva(
        "R001", cliente1, sala, 2
    )

    if reserva1:
        reserva1.procesar()

    print("\nOPERACION 9: Crear reserva de equipo")
    reserva2 = sistema.crear_reserva(
        "R002", cliente2, equipo, 3
    )

    if reserva2:
        reserva2.procesar()

    print("\nOPERACION 10: Intentar reserva con duracion invalida")
    sistema.crear_reserva(
        "R003", cliente1, asesoria, 0
    )

    print("\nOPERACION 11: Cancelar una reserva")
    if reserva2:
        try:
            reserva2.cancelar()
            print("Reserva cancelada correctamente.")
        except ErrorSistema as error:
            logging.error(str(error))
            print("Error:", error)

    print("\nOPERACION 12: Intentar reservar servicio no disponible")
    sala.disponible = False
    sistema.crear_reserva(
        "R004", cliente1, sala, 1
    )

    print("\nOPERACION 13: Calcular costo con impuesto y descuento")
    costo = asesoria.calcular_costo(
        cantidad=2, impuesto=19, descuento=10000
    )
    print(f"Costo total de asesoria: ${costo:,.2f}")

    sistema.mostrar_clientes()
    sistema.mostrar_servicios()
    sistema.mostrar_reservas()

    print("\n" + "=" * 55)
    print("PROGRAMA FINALIZADO CORRECTAMENTE")
    print("Los eventos y errores se registraron en logs.txt")
    print("=" * 55)


# =====================================================
# INICIO DEL PROGRAMA
# =====================================================

if __name__ == "__main__":
    try:
        ejecutar_sistema()

    except Exception as error:
        logging.critical(f"Error inesperado: {error}")
        print("Se presento un error inesperado:", error)
