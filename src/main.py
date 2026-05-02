# Aporte Yorlan Rivera 
import os                          # Operaciones del sistema de archivos
import re                          # Expresiones regulares para validaciones
import uuid                        # Generación de identificadores únicos
import logging                     # Módulo de registro de eventos y errores
from abc import ABC, abstractmethod  # Clases abstractas
from datetime import datetime        # Manejo de fechas y horas
from typing import Optional, List    # Anotaciones de tipo
 
 

# SECCIÓN 1: CONFIGURACIÓN DEL SISTEMA DE LOGS

 
def configurar_logger() -> logging.Logger:
    """
    Configura y retorna el logger principal del sistema.
    Escribe tanto en consola como en el archivo 'sistema_fj.log'.
    """
    # Crear el logger con el nombre de la aplicación
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.DEBUG)   # Capturar todos los niveles de mensaje
 
    # Formato detallado para cada entrada del log
    formato = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
 
    #  Handler para escribir en archivo
    manejador_archivo = logging.FileHandler("sistema_fj.log", encoding="utf-8")
    manejador_archivo.setLevel(logging.DEBUG)   # Registrar todo en el archivo
    manejador_archivo.setFormatter(formato)
 
    #  Handler para mostrar en consola 
    manejador_consola = logging.StreamHandler()
    manejador_consola.setLevel(logging.INFO)    # Solo INFO o superior en consola
    manejador_consola.setFormatter(formato)
 
    # Agregar los dos handlers al logger
    logger.addHandler(manejador_archivo)
    logger.addHandler(manejador_consola)
 
    return logger
 
 
# Instancia global del logger (disponible en todo el módulo)
logger = configurar_logger()
 
 

# SECCIÓN 2: EXCEPCIONES PERSONALIZADAS

 
class ErrorSistemaFJ(Exception):
    """
    Excepción base del sistema. Todas las excepciones personalizadas
    heredan de esta clase para facilitar capturas genéricas.
    """
    def __init__(self, mensaje: str, codigo: int = 0):
        super().__init__(mensaje)          # Inicializar la excepción padre
        self.codigo = codigo               # Código numérico del error
        self.timestamp = datetime.now()    # Momento exacto del error
 
    def __str__(self) -> str:
        # Representación legible de la excepción
        return f"[Código {self.codigo}] {super().__str__()}"
 
 
class ErrorValidacionCliente(ErrorSistemaFJ):
    """Excepción lanzada cuando los datos de un cliente no son válidos."""
    def __init__(self, campo: str, valor: str, razon: str):
        mensaje = f"Validación fallida en cliente | Campo: '{campo}' | Valor: '{valor}' | Razón: {razon}"
        super().__init__(mensaje, codigo=100)
        self.campo = campo    # Nombre del campo que falló
        self.valor = valor    # Valor que causó el error
 
 
class ErrorServicioNoDisponible(ErrorSistemaFJ):
    """Excepción lanzada cuando un servicio no puede procesarse."""
    def __init__(self, nombre_servicio: str, razon: str):
        mensaje = f"Servicio no disponible: '{nombre_servicio}' | Razón: {razon}"
        super().__init__(mensaje, codigo=200)
        self.nombre_servicio = nombre_servicio
 
 
class ErrorReservaInvalida(ErrorSistemaFJ):
    """Excepción lanzada cuando una reserva no cumple las condiciones requeridas."""
    def __init__(self, razon: str, id_reserva: str = "N/A"):
        mensaje = f"Reserva inválida [ID: {id_reserva}] | Razón: {razon}"
        super().__init__(mensaje, codigo=300)
        self.id_reserva = id_reserva
 
 
class ErrorParametroFaltante(ErrorSistemaFJ):
    """Excepción lanzada cuando falta un parámetro obligatorio."""
    def __init__(self, parametro: str, contexto: str):
        mensaje = f"Parámetro faltante: '{parametro}' en contexto '{contexto}'"
        super().__init__(mensaje, codigo=400)
        self.parametro = parametro
 
 
class ErrorOperacionNoPermitida(ErrorSistemaFJ):
    """Excepción lanzada cuando se intenta una operación no permitida."""
    def __init__(self, operacion: str, razon: str):
        mensaje = f"Operación no permitida: '{operacion}' | Razón: {razon}"
        super().__init__(mensaje, codigo=500)
        self.operacion = operacion
 
 
class ErrorCalculoCosto(ErrorSistemaFJ):
    """Excepción lanzada cuando hay inconsistencias en el cálculo de costos."""
    def __init__(self, detalle: str):
        mensaje = f"Error en cálculo de costo: {detalle}"
        super().__init__(mensaje, codigo=600)
 
 

# SECCIÓN 3: CLASE ABSTRACTA BASE DEL SISTEMA

 
class EntidadSistema(ABC):
    """
    Clase abstracta base que representa cualquier entidad dentro del sistema.
    Define la interfaz mínima que deben implementar todas las entidades.
    Aplica el principio de ABSTRACCIÓN.
    """
 
    def __init__(self, nombre: str):
        # Validar que el nombre no esté vacío antes de asignarlo
        if not nombre or not nombre.strip():
            raise ErrorParametroFaltante("nombre", self.__class__.__name__)
        self._id = str(uuid.uuid4())[:8].upper()  # ID único de 8 caracteres
        self._nombre = nombre.strip()              # Nombre sin espacios extremos
        self._fecha_creacion = datetime.now()      # Fecha de registro en sistema
 
    #  Propiedades de solo lectura 
    @property
    def id(self) -> str:
        """Retorna el identificador único de la entidad."""
        return self._id
 
    @property
    def nombre(self) -> str:
        """Retorna el nombre de la entidad."""
        return self._nombre
 
    @property
    def fecha_creacion(self) -> datetime:
        """Retorna la fecha en que fue creada la entidad."""
        return self._fecha_creacion
 
    #  Métodos abstractos que deben implementar las subclases 
    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción detallada de la entidad."""
        pass
 
    @abstractmethod
    def validar(self) -> bool:
        """Verifica que la entidad tiene datos coherentes. Retorna True si es válida."""
        pass
 
    def __repr__(self) -> str:
        # Representación técnica del objeto
        return f"{self.__class__.__name__}(id={self._id}, nombre='{self._nombre}')"
 
 

# SECCIÓN 4: CLASE CLIENTE

 
class Cliente(EntidadSistema):
    """
    Representa un cliente de la empresa Software FJ.
    Aplica ENCAPSULACIÓN: todos los atributos son privados y se acceden
    mediante propiedades con validaciones.
    Hereda de EntidadSistema (HERENCIA).
    """
 
    # Patrón de correo electrónico válido
    _PATRON_EMAIL = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
    # Patrón de teléfono: solo dígitos, entre 7 y 15 caracteres
    _PATRON_TELEFONO = re.compile(r"^\d{7,15}$")
 
    def __init__(self, nombre: str, email: str, telefono: str, tipo: str = "regular"):
        """
        Inicializa un cliente con validación estricta de todos sus campos.
 
        Args:
            nombre   : Nombre completo del cliente.
            email    : Correo electrónico válido.
            telefono : Número telefónico (solo dígitos, 7-15 caracteres).
            tipo     : Categoría del cliente ('regular', 'premium', 'corporativo').
        """
        super().__init__(nombre)          # Llamar al constructor de la clase base
 
        # Asignar atributos privados usando los setters que ya validan
        self.email = email                # Usa el setter definido abajo
        self.telefono = telefono          # Usa el setter definido abajo
        self.tipo = tipo                  # Usa el setter definido abajo
 
        # Lista interna de IDs de reservas asociadas al cliente
        self._reservas: List[str] = []
 
        logger.debug(f"Cliente creado exitosamente: {self._nombre} (ID: {self._id})")
 
    #  Propiedad: email 
    @property
    def email(self) -> str:
        return self._email
 
    @email.setter
    def email(self, valor: str):
        # Verificar que el valor no sea vacío
        if not valor or not valor.strip():
            raise ErrorValidacionCliente("email", str(valor), "El email no puede estar vacío")
        valor = valor.strip().lower()   # Normalizar a minúsculas
        # Verificar formato con expresión regular
        if not self._PATRON_EMAIL.match(valor):
            raise ErrorValidacionCliente("email", valor, "Formato de email inválido (ej: usuario@dominio.com)")
        self._email = valor             # Asignar el valor validado
 
    #  Propiedad: teléfono 
    @property
    def telefono(self) -> str:
        return self._telefono
 
    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not str(valor).strip():
            raise ErrorValidacionCliente("telefono", str(valor), "El teléfono no puede estar vacío")
        valor = str(valor).strip().replace(" ", "").replace("-", "")  # Limpiar espacios y guiones
        if not self._PATRON_TELEFONO.match(valor):
            raise ErrorValidacionCliente("telefono", valor, "Solo dígitos, entre 7 y 15 caracteres")
        self._telefono = valor
 
    # Propiedad: tipo 
    @property
    def tipo(self) -> str:
        return self._tipo
 
    @tipo.setter
    def tipo(self, valor: str):
        tipos_validos = {"regular", "premium", "corporativo"}   # Tipos permitidos
        if valor.lower() not in tipos_validos:
            raise ErrorValidacionCliente(
                "tipo", valor,
                f"Tipo inválido. Opciones válidas: {tipos_validos}"
            )
        self._tipo = valor.lower()
 
    #  Métodos abstractos implementados 
    def describir(self) -> str:
        """Retorna descripción completa del cliente."""
        return (
            f"CLIENTE │ ID: {self._id} │ Nombre: {self._nombre} │ "
            f"Email: {self._email} │ Teléfono: {self._telefono} │ "
            f"Tipo: {self._tipo.upper()} │ Reservas: {len(self._reservas)}"
        )
 
    def validar(self) -> bool:
        """Verifica que el cliente tiene todos sus datos correctos."""
        return bool(
            self._nombre and
            self._email and
            self._telefono and
            self._tipo
        )
 
    #  Métodos de gestión de reservas 
    def agregar_reserva(self, id_reserva: str):
        """Registra el ID de una nueva reserva en la lista del cliente."""
        if id_reserva not in self._reservas:
            self._reservas.append(id_reserva)
 
    def obtener_reservas(self) -> List[str]:
        """Retorna la lista de IDs de reservas del cliente."""
        return list(self._reservas)    # Retornar copia para proteger la lista interna
 
    def descuento_por_tipo(self) -> float:
        """
        Retorna el porcentaje de descuento según el tipo de cliente.
        regular=0%, premium=10%, corporativo=20%.
        """
        descuentos = {"regular": 0.0, "premium": 0.10, "corporativo": 0.20}
        return descuentos.get(self._tipo, 0.0)
 
 

# SECCIÓN 5: CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS

 
class Servicio(EntidadSistema, ABC):
    """
    Clase abstracta que representa un servicio ofrecido por Software FJ.
    Define la interfaz común de todos los servicios.
    Aplica ABSTRACCIÓN y sirve como base para HERENCIA.
    """
 
    # Impuesto IVA aplicado a todos los servicios
    IVA = 0.19   # 19%
 
    def __init__(self, nombre: str, precio_base: float, disponible: bool = True):
        """
        Args:
            nombre      : Nombre del servicio.
            precio_base : Costo base del servicio en pesos colombianos.
            disponible  : Indica si el servicio está activo.
        """
        super().__init__(nombre)
 
        # Validar que el precio sea un número positivo
        if not isinstance(precio_base, (int, float)) or precio_base <= 0:
            raise ErrorServicioNoDisponible(
                nombre,
                f"El precio base debe ser un número positivo. Se recibió: {precio_base}"
            )
 
        self._precio_base = float(precio_base)   # Precio en pesos colombianos
        self._disponible = disponible            # Estado del servicio
 
    #  Propiedades 
    @property
    def precio_base(self) -> float:
        return self._precio_base
 
    @property
    def disponible(self) -> bool:
        return self._disponible
 
    @disponible.setter
    def disponible(self, valor: bool):
        self._disponible = bool(valor)
 
    #  Método sobrecargado: calcular_costo 
    # Python no soporta sobrecarga nativa, se simula con parámetros opcionales.
 
    def calcular_costo(
        self,
        horas: float,
        aplicar_iva: bool = False,
        descuento: float = 0.0,
        costo_adicional: float = 0.0
    ) -> float:
        """
        Calcula el costo total del servicio. Método sobrecargado mediante
        parámetros opcionales que permiten múltiples combinaciones de uso.
 
        Variantes de uso (polimorfismo de parámetros):
          1. calcular_costo(horas)                    → costo base × horas
          2. calcular_costo(horas, aplicar_iva=True)  → + IVA
          3. calcular_costo(horas, descuento=0.10)    → - 10% descuento
          4. calcular_costo(horas, True, 0.10, 5000)  → todo incluido
 
        Args:
            horas           : Número de horas del servicio.
            aplicar_iva     : Si True, agrega el 19% de IVA.
            descuento       : Fracción de descuento (0.0 a 0.99).
            costo_adicional : Costo extra a sumar (ej: materiales).
 
        Returns:
            float: Costo total calculado.
 
        Raises:
            ErrorCalculoCosto: Si los parámetros son incoherentes.
        """
        # Validaciones de entrada 
        if horas <= 0:
            raise ErrorCalculoCosto(f"Las horas deben ser positivas. Se recibió: {horas}")
        if not (0.0 <= descuento < 1.0):
            raise ErrorCalculoCosto(f"El descuento debe estar entre 0.0 y 0.99. Se recibió: {descuento}")
        if costo_adicional < 0:
            raise ErrorCalculoCosto(f"El costo adicional no puede ser negativo. Se recibió: {costo_adicional}")
 
        # Cálculo paso a paso 
        subtotal = self._calcular_costo_especifico(horas)    # Delegar al servicio específico
        subtotal += costo_adicional                          # Sumar costos extras
 
        if descuento > 0:                                    # Aplicar descuento si existe
            subtotal -= subtotal * descuento
 
        if aplicar_iva:                                      # Aplicar IVA si se solicita
            subtotal += subtotal * self.IVA
 
        return round(subtotal, 2)    # Redondear a 2 decimales
 
    @abstractmethod
    def _calcular_costo_especifico(self, horas: float) -> float:
        """
        Cada servicio especializado define su propia fórmula de costo.
        Aplica POLIMORFISMO.
        """
        pass
 
    def verificar_disponibilidad(self):
        """
        Verifica que el servicio esté disponible.
        Lanza excepción si no lo está.
        """
        if not self._disponible:
            raise ErrorServicioNoDisponible(
                self._nombre,
                "El servicio está marcado como no disponible en este momento"
            )
 
 

# SERVICIO 1: Reserva de Sala

 
class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reunión o trabajo.
    Hereda de Servicio e implementa su propia lógica de costo.
    """
 
    def __init__(self, nombre: str, capacidad: int, precio_hora: float, disponible: bool = True):
        """
        Args:
            nombre      : Nombre identificador de la sala.
            capacidad   : Número máximo de personas.
            precio_hora : Costo por hora de uso.
            disponible  : Estado de disponibilidad.
        """
        super().__init__(nombre, precio_hora, disponible)
 
        # Validar capacidad
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ErrorServicioNoDisponible(nombre, f"Capacidad inválida: {capacidad}. Debe ser entero positivo.")
        self._capacidad = capacidad     # Capacidad máxima de personas
 
    @property
    def capacidad(self) -> int:
        return self._capacidad
 
    def _calcular_costo_especifico(self, horas: float) -> float:
        """Costo = precio_hora × horas. Sin recargos adicionales."""
        return self._precio_base * horas
 
    def describir(self) -> str:
        estado = "✔ Disponible" if self._disponible else "✘ No disponible"
        return (
            f"SALA │ ID: {self._id} │ Nombre: {self._nombre} │ "
            f"Capacidad: {self._capacidad} personas │ "
            f"Precio/hora: ${self._precio_base:,.0f} COP │ Estado: {estado}"
        )
 
    def validar(self) -> bool:
        return self._capacidad > 0 and self._precio_base > 0
 
 

# SERVICIO 2: Alquiler de Equipos

 
class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    Aplica un recargo por mantenimiento del 5% sobre el subtotal.
    """
 
    RECARGO_MANTENIMIENTO = 0.05   # 5% adicional por mantenimiento
 
    def __init__(self, nombre: str, tipo_equipo: str, precio_hora: float,
                 stock: int = 1, disponible: bool = True):
        """
        Args:
            nombre      : Nombre del equipo.
            tipo_equipo : Categoría (laptop, proyector, servidor, etc.).
            precio_hora : Costo de alquiler por hora.
            stock       : Unidades disponibles para alquilar.
            disponible  : Estado del servicio.
        """
        super().__init__(nombre, precio_hora, disponible)
 
        if not tipo_equipo or not tipo_equipo.strip():
            raise ErrorServicioNoDisponible(nombre, "El tipo de equipo no puede estar vacío")
        if not isinstance(stock, int) or stock < 0:
            raise ErrorServicioNoDisponible(nombre, f"Stock inválido: {stock}")
 
        self._tipo_equipo = tipo_equipo.strip()   # Categoría del equipo
        self._stock = stock                       # Unidades disponibles
 
    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo
 
    @property
    def stock(self) -> int:
        return self._stock
 
    def reducir_stock(self, cantidad: int = 1):
        """Reduce el stock al realizar un alquiler."""
        if self._stock < cantidad:
            raise ErrorServicioNoDisponible(
                self._nombre,
                f"Stock insuficiente. Disponible: {self._stock}, Solicitado: {cantidad}"
            )
        self._stock -= cantidad
 
    def _calcular_costo_especifico(self, horas: float) -> float:
        """Costo = (precio_hora × horas) + 5% recargo de mantenimiento."""
        subtotal = self._precio_base * horas
        recargo = subtotal * self.RECARGO_MANTENIMIENTO    # Aplicar recargo
        return subtotal + recargo
 
    def describir(self) -> str:
        estado = "✔ Disponible" if self._disponible else "✘ No disponible"
        return (
            f"EQUIPO │ ID: {self._id} │ Nombre: {self._nombre} │ "
            f"Tipo: {self._tipo_equipo} │ Stock: {self._stock} │ "
            f"Precio/hora: ${self._precio_base:,.0f} COP │ Estado: {estado}"
        )
 
    def validar(self) -> bool:
        return bool(self._tipo_equipo) and self._precio_base > 0 and self._stock >= 0
 
 

# SERVICIO 3: Asesoría Especializada

 
class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría técnica o profesional.
    Aplica tarifas diferenciadas según la especialidad del asesor.
    """
 
    # Multiplicadores de tarifa según nivel de especialidad
    NIVELES = {
        "junior": 1.0,       # Sin recargo
        "senior": 1.5,       # 50% más caro
        "experto": 2.0       # Doble de precio
    }
 
    def __init__(self, nombre: str, especialidad: str, precio_hora: float,
                 nivel: str = "junior", disponible: bool = True):
        """
        Args:
            nombre       : Nombre descriptivo de la asesoría.
            especialidad : Área temática (sistemas, redes, datos, etc.).
            precio_hora  : Tarifa base por hora.
            nivel        : Nivel del asesor (junior, senior, experto).
            disponible   : Estado del servicio.
        """
        super().__init__(nombre, precio_hora, disponible)
 
        if not especialidad or not especialidad.strip():
            raise ErrorServicioNoDisponible(nombre, "La especialidad no puede estar vacía")
        if nivel.lower() not in self.NIVELES:
            raise ErrorServicioNoDisponible(
                nombre,
                f"Nivel inválido: '{nivel}'. Opciones: {list(self.NIVELES.keys())}"
            )
 
        self._especialidad = especialidad.strip()   # Área de conocimiento
        self._nivel = nivel.lower()                 # Nivel de experiencia
 
    @property
    def especialidad(self) -> str:
        return self._especialidad
 
    @property
    def nivel(self) -> str:
        return self._nivel
 
    def _calcular_costo_especifico(self, horas: float) -> float:
        """Costo = precio_hora × horas × multiplicador_nivel."""
        multiplicador = self.NIVELES[self._nivel]     # Obtener factor según nivel
        return self._precio_base * horas * multiplicador
 
    def describir(self) -> str:
        estado = "✔ Disponible" if self._disponible else "✘ No disponible"
        multiplicador = self.NIVELES[self._nivel]
        return (
            f"ASESORÍA │ ID: {self._id} │ Nombre: {self._nombre} │ "
            f"Especialidad: {self._especialidad} │ Nivel: {self._nivel.upper()} │ "
            f"Precio/hora: ${self._precio_base:,.0f} COP (×{multiplicador}) │ Estado: {estado}"
        )
 
    def validar(self) -> bool:
        return bool(self._especialidad) and self._nivel in self.NIVELES and self._precio_base > 0
 
 

# SECCIÓN 6: CLASE RESERVA

 
class Reserva:
    """
    Representa una reserva que integra un cliente, un servicio y una duración.
    Maneja los estados del ciclo de vida: PENDIENTE → CONFIRMADA → CANCELADA.
    Aplica manejo robusto de excepciones en cada operación.
    """
 
    # Estados válidos del ciclo de vida de una reserva
    ESTADOS = {"pendiente", "confirmada", "cancelada", "procesada"}
 
    def __init__(self, cliente: Cliente, servicio: Servicio, horas: float,
                 aplicar_iva: bool = False, descuento_extra: float = 0.0):
        """
        Args:
            cliente        : Objeto Cliente que realiza la reserva.
            servicio       : Objeto Servicio a reservar.
            horas          : Duración de la reserva en horas.
            aplicar_iva    : Si True, incluir IVA en el costo total.
            descuento_extra: Descuento adicional sobre el total (fracción).
        """
        #  Validaciones de entrada 
        if not isinstance(cliente, Cliente):
            raise ErrorReservaInvalida("El cliente proporcionado no es un objeto Cliente válido")
        if not isinstance(servicio, Servicio):
            raise ErrorReservaInvalida("El servicio proporcionado no es un objeto Servicio válido")
        if horas <= 0:
            raise ErrorReservaInvalida(f"La duración debe ser positiva. Se recibió: {horas} horas")
 
        self._id = str(uuid.uuid4())[:8].upper()     # ID único de la reserva
        self._cliente = cliente                       # Referencia al cliente
        self._servicio = servicio                     # Referencia al servicio
        self._horas = float(horas)                   # Duración en horas
        self._aplicar_iva = aplicar_iva              # Flag de IVA
        self._descuento_extra = descuento_extra      # Descuento adicional
        self._estado = "pendiente"                   # Estado inicial
        self._fecha_creacion = datetime.now()        # Fecha de creación
        self._fecha_proceso: Optional[datetime] = None  # Fecha de procesamiento
        self._costo_total: float = 0.0              # Se calcula al confirmar
        self._notas: str = ""                       # Notas opcionales
 
        logger.info(f"Reserva creada [ID: {self._id}] | Cliente: {cliente.nombre} | Servicio: {servicio.nombre}")
 
    #  Propiedades de solo lectura 
    @property
    def id(self) -> str:
        return self._id
 
    @property
    def estado(self) -> str:
        return self._estado
 
    @property
    def costo_total(self) -> float:
        return self._costo_total
 
    @property
    def cliente(self) -> Cliente:
        return self._cliente
 
    @property
    def servicio(self) -> Servicio:
        return self._servicio
 
    #  Confirmar reserva 
    def confirmar(self) -> float:
        """
        Confirma la reserva: verifica disponibilidad y calcula el costo.
 
        Returns:
            float: Costo total de la reserva confirmada.
 
        Raises:
            ErrorOperacionNoPermitida : Si la reserva no está en estado 'pendiente'.
            ErrorServicioNoDisponible : Si el servicio no está disponible.
            ErrorCalculoCosto         : Si falla el cálculo del costo.
        """
        try:
            # Verificar que la reserva esté en el estado correcto
            if self._estado != "pendiente":
                raise ErrorOperacionNoPermitida(
                    "confirmar",
                    f"Solo se pueden confirmar reservas en estado 'pendiente'. Estado actual: '{self._estado}'"
                )
 
            # Verificar que el servicio esté disponible
            self._servicio.verificar_disponibilidad()
 
            # Calcular el descuento combinado: tipo de cliente + descuento extra
            descuento_cliente = self._cliente.descuento_por_tipo()
            descuento_total = min(descuento_cliente + self._descuento_extra, 0.99)  # Máximo 99%
 
            # Calcular el costo total usando el método sobrecargado
            self._costo_total = self._servicio.calcular_costo(
                horas=self._horas,
                aplicar_iva=self._aplicar_iva,
                descuento=descuento_total
            )
 
            self._estado = "confirmada"          # Actualizar estado
            logger.info(
                f"Reserva CONFIRMADA [ID: {self._id}] | "
                f"Costo: ${self._costo_total:,.2f} COP | "
                f"Descuento aplicado: {descuento_total*100:.0f}%"
            )
            return self._costo_total
 
        except (ErrorOperacionNoPermitida, ErrorServicioNoDisponible, ErrorCalculoCosto):
            logger.error(f"Error al confirmar reserva [ID: {self._id}]", exc_info=True)
            raise    # Re-lanzar para que el llamador decida cómo manejarlo
 
        except Exception as e:
            # Encadenamiento de excepciones: convertir error genérico en específico
            raise ErrorReservaInvalida(
                f"Error inesperado al confirmar: {str(e)}",
                id_reserva=self._id
            ) from e    # Mantener la excepción original como causa
 
    #  Cancelar reserva 
    def cancelar(self, motivo: str = "Sin motivo especificado") -> bool:
        """
        Cancela la reserva. No se puede cancelar si ya fue procesada.
 
        Args:
            motivo: Razón de la cancelación.
 
        Returns:
            bool: True si se canceló exitosamente.
        """
        try:
            # Verificar que el estado permita cancelación
            if self._estado == "procesada":
                raise ErrorOperacionNoPermitida(
                    "cancelar",
                    "No se puede cancelar una reserva que ya fue procesada"
                )
            if self._estado == "cancelada":
                raise ErrorOperacionNoPermitida(
                    "cancelar",
                    "La reserva ya está cancelada"
                )
 
            self._estado = "cancelada"    # Actualizar estado
            self._notas = f"Cancelada: {motivo}"
            logger.warning(f"Reserva CANCELADA [ID: {self._id}] | Motivo: {motivo}")
            return True
 
        except ErrorOperacionNoPermitida as e:
            logger.error(f"No se pudo cancelar reserva [ID: {self._id}]: {e}")
            raise
 
    #  Procesar reserva 
    def procesar(self) -> bool:
        """
        Marca la reserva como procesada (servicio ejecutado).
        Solo se pueden procesar reservas confirmadas.
 
        Returns:
            bool: True si el procesamiento fue exitoso.
        """
        try:
            if self._estado != "confirmada":
                raise ErrorOperacionNoPermitida(
                    "procesar",
                    f"Solo se pueden procesar reservas 'confirmadas'. Estado actual: '{self._estado}'"
                )
 
            self._estado = "procesada"               # Actualizar estado final
            self._fecha_proceso = datetime.now()     # Registrar fecha de ejecución
 
            # Registrar la reserva en el historial del cliente
            self._cliente.agregar_reserva(self._id)
 
            logger.info(
                f"Reserva PROCESADA [ID: {self._id}] | "
                f"Cliente: {self._cliente.nombre} | "
                f"Servicio: {self._servicio.nombre} | "
                f"Costo final: ${self._costo_total:,.2f} COP"
            )
            return True
 
        except ErrorOperacionNoPermitida as e:
            logger.error(f"Error al procesar reserva [ID: {self._id}]: {e}")
            raise
 
        finally:
            # El bloque finally siempre se ejecuta, independientemente del resultado
            logger.debug(f"Intento de procesamiento finalizado para reserva [ID: {self._id}]")
 
    #  Representación textual 
    def describir(self) -> str:
        """Retorna un resumen completo de la reserva."""
        iconos_estado = {
            "pendiente": "⏳", "confirmada": "✅",
            "cancelada": "❌", "procesada": "🏁"
        }
        icono = iconos_estado.get(self._estado, "?")
        return (
            f"RESERVA {icono} │ ID: {self._id} │ Estado: {self._estado.upper()} │\n"
            f"  Cliente : {self._cliente.nombre} ({self._cliente.tipo})\n"
            f"  Servicio: {self._servicio.nombre}\n"
            f"  Duración: {self._horas}h │ IVA: {'Sí' if self._aplicar_iva else 'No'}\n"
            f"  Costo   : ${self._costo_total:,.2f} COP\n"
            f"  Creada  : {self._fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}"
        )
 
 

# SECCIÓN 7: GESTOR DEL SISTEMA

 
class SistemaGestion:
    """
    Clase principal que orquesta todas las operaciones del sistema.
    Mantiene las listas internas de clientes, servicios y reservas.
    Centraliza el manejo de excepciones y el registro de eventos.
    """
 
    def __init__(self):
        # Listas internas que reemplazan la base de datos
        self._clientes: List[Cliente] = []      # Registro de clientes
        self._servicios: List[Servicio] = []    # Catálogo de servicios
        self._reservas: List[Reserva] = []      # Historial de reservas
 
        logger.info("═" * 60)
        logger.info("SISTEMA DE GESTIÓN SOFTWARE FJ - INICIADO")
        logger.info("═" * 60)
 
    #  Gestión de Clientes 
 
    def registrar_cliente(self, nombre: str, email: str, telefono: str,
                          tipo: str = "regular") -> Optional[Cliente]:
        """
        Registra un nuevo cliente. Usa try/except/else para diferenciar
        el flujo exitoso del fallido.
        """
        try:
            # Verificar email duplicado antes de crear
            for c in self._clientes:
                if c.email == email.strip().lower():
                    raise ErrorValidacionCliente(
                        "email", email,
                        "Ya existe un cliente registrado con este email"
                    )
            # Intentar crear el cliente (puede lanzar excepciones de validación)
            nuevo_cliente = Cliente(nombre, email, telefono, tipo)
 
        except ErrorValidacionCliente as e:
            # Manejo específico de errores de validación
            logger.error(f"Registro de cliente FALLIDO: {e}")
            return None    # Retornar None indica fallo sin interrumpir el programa
 
        except ErrorParametroFaltante as e:
            logger.error(f"Registro de cliente FALLIDO (parámetro faltante): {e}")
            return None
 
        except Exception as e:
            # Captura genérica para errores inesperados
            logger.critical(f"Error inesperado al registrar cliente: {e}", exc_info=True)
            return None
 
        else:
            # El bloque else solo se ejecuta si NO hubo excepciones
            self._clientes.append(nuevo_cliente)
            logger.info(f"Cliente REGISTRADO: {nuevo_cliente.nombre} [ID: {nuevo_cliente.id}]")
            return nuevo_cliente
 
    def buscar_cliente_por_email(self, email: str) -> Optional[Cliente]:
        """Busca y retorna un cliente por su email. Retorna None si no existe."""
        email_normalizado = email.strip().lower()
        for cliente in self._clientes:
            if cliente.email == email_normalizado:
                return cliente
        return None
 
    #  Gestión de Servicios 
 
    def registrar_servicio(self, servicio: Servicio) -> bool:
        """
        Registra un servicio en el catálogo del sistema.
        Valida que el servicio sea coherente antes de agregarlo.
        """
        try:
            # Verificar que el objeto es un Servicio válido
            if not isinstance(servicio, Servicio):
                raise ErrorParametroFaltante("servicio", "registrar_servicio")
 
            # Ejecutar la validación interna del servicio
            if not servicio.validar():
                raise ErrorServicioNoDisponible(
                    servicio.nombre,
                    "El servicio no pasó la validación interna"
                )
 
            # Verificar nombre duplicado
            for s in self._servicios:
                if s.nombre.lower() == servicio.nombre.lower():
                    raise ErrorServicioNoDisponible(
                        servicio.nombre,
                        "Ya existe un servicio con ese nombre"
                    )
 
        except (ErrorParametroFaltante, ErrorServicioNoDisponible) as e:
            logger.error(f"Registro de servicio FALLIDO: {e}")
            return False
 
        else:
            # Solo se ejecuta si no hubo errores
            self._servicios.append(servicio)
            logger.info(f"Servicio REGISTRADO: {servicio.nombre} [ID: {servicio.id}]")
            return True
 
        # Nota: finally aquí registraría el intento siempre (no es necesario para este caso)
 
    def buscar_servicio_por_nombre(self, nombre: str) -> Optional[Servicio]:
        """Busca un servicio por nombre (insensible a mayúsculas). Retorna None si no existe."""
        nombre_lower = nombre.strip().lower()
        for servicio in self._servicios:
            if servicio.nombre.lower() == nombre_lower:
                return servicio
        return None
 
    # Gestión de Reservas
 
    def crear_reserva(self, email_cliente: str, nombre_servicio: str,
                      horas: float, aplicar_iva: bool = False,
                      descuento_extra: float = 0.0) -> Optional[Reserva]:
        """
        Crea una nueva reserva vinculando cliente y servicio.
        Demuestra el uso de try/except/finally.
        """
        reserva = None     # Inicializar para poder usar en finally
 
        try:
            #  Buscar cliente 
            cliente = self.buscar_cliente_por_email(email_cliente)
            if not cliente:
                raise ErrorReservaInvalida(
                    f"No se encontró cliente con email: '{email_cliente}'"
                )
 
            # Buscar servicio 
            servicio = self.buscar_servicio_por_nombre(nombre_servicio)
            if not servicio:
                raise ErrorReservaInvalida(
                    f"No se encontró servicio con nombre: '{nombre_servicio}'"
                )
 
            # Crear la reserva 
            reserva = Reserva(cliente, servicio, horas, aplicar_iva, descuento_extra)
            self._reservas.append(reserva)    # Agregar a la lista interna
            return reserva
 
        except ErrorReservaInvalida as e:
            logger.error(f"Creación de reserva FALLIDA: {e}")
            return None
 
        except Exception as e:
            logger.critical(f"Error inesperado al crear reserva: {e}", exc_info=True)
            return None
 
        finally:
            # Este bloque se ejecuta SIEMPRE (haya error o no)
            estado_final = reserva.estado if reserva else "no creada"
            logger.debug(
                f"Intento de crear reserva finalizado | "
                f"Cliente: {email_cliente} | Servicio: {nombre_servicio} | "
                f"Estado: {estado_final}"
            )
 
    def confirmar_reserva(self, id_reserva: str) -> bool:
        """Busca una reserva por ID y la confirma."""
        reserva = self._buscar_reserva(id_reserva)
        if not reserva:
            logger.error(f"Confirmar reserva FALLIDO: ID '{id_reserva}' no encontrado")
            return False
        try:
            costo = reserva.confirmar()
            print(f"  ✅ Reserva {id_reserva} confirmada → Costo: ${costo:,.2f} COP")
            return True
        except ErrorSistemaFJ as e:
            logger.error(f"No se pudo confirmar reserva [{id_reserva}]: {e}")
            return False
 
    def cancelar_reserva(self, id_reserva: str, motivo: str = "") -> bool:
        """Busca una reserva por ID y la cancela."""
        reserva = self._buscar_reserva(id_reserva)
        if not reserva:
            logger.error(f"Cancelar reserva FALLIDO: ID '{id_reserva}' no encontrado")
            return False
        try:
            return reserva.cancelar(motivo or "Cancelada por el sistema")
        except ErrorSistemaFJ as e:
            logger.error(f"No se pudo cancelar reserva [{id_reserva}]: {e}")
            return False
 
    def procesar_reserva(self, id_reserva: str) -> bool:
        """Busca una reserva por ID y la procesa."""
        reserva = self._buscar_reserva(id_reserva)
        if not reserva:
            logger.error(f"Procesar reserva FALLIDO: ID '{id_reserva}' no encontrado")
            return False
        try:
            return reserva.procesar()
        except ErrorSistemaFJ as e:
            logger.error(f"No se pudo procesar reserva [{id_reserva}]: {e}")
            return False
 
    def _buscar_reserva(self, id_reserva: str) -> Optional[Reserva]:
        """Método privado: busca una reserva por su ID."""
        for reserva in self._reservas:
            if reserva.id == id_reserva.upper():
                return reserva
        return None
 
    #  Reportes del sistema 
 
    def mostrar_resumen(self):
        """Imprime un resumen del estado actual del sistema."""
        separador = "─" * 65
        print(f"\n{'═'*65}")
        print(f"  RESUMEN DEL SISTEMA - SOFTWARE FJ")
        print(f"{'═'*65}")
        print(f"  Clientes registrados : {len(self._clientes)}")
        print(f"  Servicios disponibles: {len(self._servicios)}")
        print(f"  Total de reservas    : {len(self._reservas)}")
 
        # Contar reservas por estado
        conteo = {e: 0 for e in Reserva.ESTADOS}
        for r in self._reservas:
            conteo[r.estado] = conteo.get(r.estado, 0) + 1
        for estado, cantidad in conteo.items():
            if cantidad > 0:
                print(f"    └ {estado.capitalize():12} : {cantidad}")
 
        # Calcular ingresos de reservas procesadas
        ingresos = sum(r.costo_total for r in self._reservas if r.estado == "procesada")
        print(f"  Ingresos generados   : ${ingresos:,.2f} COP")
        print(f"{'═'*65}\n")
 
 

# SECCIÓN 8: SIMULACIÓN DE OPERACIONES (MAIN)

 
def separador(titulo: str):
    """Imprime un separador visual con título para la consola."""
    print(f"\n{'─'*65}")
    print(f"  {titulo}")
    print(f"{'─'*65}")
 
 
def ejecutar_simulacion():
    """
    Ejecuta las 10+ operaciones completas que demuestra el sistema.
    Incluye casos exitosos y fallidos para probar el manejo de excepciones.
    """
    # Crear instancia del sistema
    sistema = SistemaGestion()
 
    print("\n" + "═"*65)
    print("   SISTEMA INTEGRAL - SOFTWARE FJ")
    print("   Simulación de Operaciones")
    print("═"*65)
 
    
    # OPERACIÓN 1 & 2: Registro de clientes válidos
    
    separador("OP 1-3 │ Registro de Clientes")
 
    c1 = sistema.registrar_cliente("Ana García", "ana.garcia@email.com", "3001234567", "premium")
    c2 = sistema.registrar_cliente("Carlos López", "carlos.lopez@empresa.com", "6012345678", "corporativo")
    c3 = sistema.registrar_cliente("María Torres", "maria.torres@correo.co", "3109876543", "regular")
 
    if c1: print(f"  ✅ {c1.describir()}")
    if c2: print(f"  ✅ {c2.describir()}")
    if c3: print(f"  ✅ {c3.describir()}")
 
    
    # OPERACIÓN 3: Intentos de registro INVÁLIDOS (prueban las excepciones)
    
    separador("OP 4-5 │ Registro de Clientes INVÁLIDOS")
 
    # Email con formato incorrecto
    r1 = sistema.registrar_cliente("Pedro Inválido", "correo_malo", "123456789", "regular")
    print(f"  {'✅' if r1 else '❌'} Registro con email inválido → {'Creado' if r1 else 'Rechazado (esperado)'}")
 
    # Email duplicado
    r2 = sistema.registrar_cliente("Ana Copia", "ana.garcia@email.com", "3007654321", "regular")
    print(f"  {'✅' if r2 else '❌'} Registro con email duplicado → {'Creado' if r2 else 'Rechazado (esperado)'}")
 
    # Tipo de cliente inválido
    r3 = sistema.registrar_cliente("Luis Prueba", "luis@test.com", "3001111111", "vip_especial")
    print(f"  {'✅' if r3 else '❌'} Registro con tipo inválido → {'Creado' if r3 else 'Rechazado (esperado)'}")
 
    
    # OPERACIÓN 4 & 5: Registro de servicios válidos
    
    separador("OP 6-8 │ Creación de Servicios")
 
    try:
        # Crear sala de reuniones
        sala_a = ReservaSala("Sala Innovación", capacidad=10, precio_hora=80000)
        sistema.registrar_servicio(sala_a)
        print(f"  ✅ {sala_a.describir()}")
 
        # Crear servicio de alquiler de laptop
        laptop = AlquilerEquipo("Laptop HP ProBook", tipo_equipo="Laptop", precio_hora=25000, stock=5)
        sistema.registrar_servicio(laptop)
        print(f"  ✅ {laptop.describir()}")
 
        # Crear servicio de asesoría experta en datos
        asesoria = AsesoriaEspecializada("Consultoría BigData", especialidad="Análisis de Datos",
                                         precio_hora=120000, nivel="experto")
        sistema.registrar_servicio(asesoria)
        print(f"  ✅ {asesoria.describir()}")
 
        # Servicio adicional para pruebas
        sala_b = ReservaSala("Sala Capacitación", capacidad=30, precio_hora=150000)
        sistema.registrar_servicio(sala_b)
        print(f"  ✅ {sala_b.describir()}")
 
    except ErrorSistemaFJ as e:
        logger.error(f"Error creando servicios: {e}")
 
    
    # OPERACIÓN 6: Intento de crear servicio con precio negativo (inválido)
    
    separador("OP 9 │ Servicio con Parámetro INVÁLIDO")
 
    try:
        servicio_malo = AlquilerEquipo("Proyector Roto", tipo_equipo="Proyector", precio_hora=-5000)
        sistema.registrar_servicio(servicio_malo)
        print("  ✅ Servicio creado (inesperado)")
    except ErrorServicioNoDisponible as e:
        print(f"  ❌ Servicio rechazado (esperado): {e}")
        logger.warning(f"Intento de servicio con precio inválido capturado: {e}")
 
    
    # OPERACIÓN 7: Crear y confirmar reservas EXITOSAS
    
    separador("OP 10-12 │ Reservas Exitosas")
 
    # Reserva 1: cliente premium, sala, 3 horas, con IVA
    res1 = sistema.crear_reserva("ana.garcia@email.com", "Sala Innovación",
                                  horas=3, aplicar_iva=True)
    if res1:
        print(f"  ✅ Reserva creada [ID: {res1.id}]")
        sistema.confirmar_reserva(res1.id)
        sistema.procesar_reserva(res1.id)
        print(res1.describir())
 
    # Reserva 2: cliente corporativo, asesoría, 2 horas, con descuento extra
    res2 = sistema.crear_reserva("carlos.lopez@empresa.com", "Consultoría BigData",
                                  horas=2, aplicar_iva=True, descuento_extra=0.05)
    if res2:
        print(f"\n  ✅ Reserva creada [ID: {res2.id}]")
        sistema.confirmar_reserva(res2.id)
        sistema.procesar_reserva(res2.id)
        print(res2.describir())
 
    # Reserva 3: cliente regular, laptop, 4 horas
    res3 = sistema.crear_reserva("maria.torres@correo.co", "Laptop HP ProBook",
                                  horas=4, aplicar_iva=False)
    if res3:
        print(f"\n  ✅ Reserva creada [ID: {res3.id}]")
        sistema.confirmar_reserva(res3.id)
        # Cancelar antes de procesar para demostrar esa operación
        sistema.cancelar_reserva(res3.id, "Cliente solicitó reprogramación")
        print(res3.describir())
 
    
    # OPERACIÓN 8: Reservas FALLIDAS (casos de error)
    
    separador("OP 13-15 │ Reservas FALLIDAS")
 
    # Reserva con cliente inexistente
    rf1 = sistema.crear_reserva("noexiste@email.com", "Sala Innovación", horas=2)
    print(f"  {'✅' if rf1 else '❌'} Reserva con cliente inexistente → {'Creada' if rf1 else 'Rechazada (esperado)'}")
 
    # Reserva con servicio inexistente
    rf2 = sistema.crear_reserva("ana.garcia@email.com", "Servicio Fantasma", horas=1)
    print(f"  {'✅' if rf2 else '❌'} Reserva con servicio inexistente → {'Creada' if rf2 else 'Rechazada (esperado)'}")
 
    # Reserva con duración negativa
    rf3 = sistema.crear_reserva("ana.garcia@email.com", "Sala Innovación", horas=-5)
    print(f"  {'✅' if rf3 else '❌'} Reserva con horas negativas → {'Creada' if rf3 else 'Rechazada (esperado)'}")
 
    
    # OPERACIÓN 9: Intentar confirmar una reserva ya procesada (error controlado)
    
    separador("OP 16 │ Operación No Permitida (Confirmar reserva ya procesada)")
 
    if res1:
        resultado = sistema.confirmar_reserva(res1.id)    # res1 ya está procesada
        print(f"  {'✅' if resultado else '❌'} Intento de re-confirmar reserva procesada → "
              f"{'Éxito' if resultado else 'Rechazado (esperado)'}")
 
    
    # OPERACIÓN 10: Calcular costos con sobrecarga de parámetros
    
    separador("OP 17 │ Demostración de Método Sobrecargado (calcular_costo)")
 
    try:
        print(f"  Variante 1 (sin opciones)   : ${sala_a.calcular_costo(2):>12,.2f} COP")
        print(f"  Variante 2 (+ IVA)          : ${sala_a.calcular_costo(2, aplicar_iva=True):>12,.2f} COP")
        print(f"  Variante 3 (+ descuento 20%): ${sala_a.calcular_costo(2, descuento=0.20):>12,.2f} COP")
        print(f"  Variante 4 (IVA + desc 10%) : ${sala_a.calcular_costo(2, True, 0.10, 10000):>12,.2f} COP")
    except ErrorCalculoCosto as e:
        logger.error(f"Error en cálculo de costo: {e}")
 
    # Intentar con parámetro inválido (descuento >= 1.0)
    try:
        sala_a.calcular_costo(2, descuento=1.5)   # Esto debe lanzar excepción
    except ErrorCalculoCosto as e:
        print(f"  ❌ Descuento inválido capturado: {e}")
 
    
    # RESUMEN FINAL
    
    sistema.mostrar_resumen()
 
    print(f"\n  📋 Todos los eventos han sido registrados en: 'sistema_fj.log'")
    print(f"  El sistema se mantuvo estable ante todos los errores.\n")
 
 

# PUNTO DE ENTRADA DEL PROGRAMA

 
if __name__ == "__main__":
    try:
        # Ejecutar la simulación completa del sistema
        ejecutar_simulacion()
    except Exception as e:
        # Captura de último recurso: no debería llegar aquí nunca
        logger.critical(f"ERROR CRÍTICO NO CONTROLADO: {e}", exc_info=True)
        print(f"\n🚨 Error crítico: {e}")
    finally:
        # Mensaje final siempre visible al terminar el programa
        logger.info("SISTEMA SOFTWARE FJ - EJECUCIÓN FINALIZADA")
        print("Ejecución del sistema finalizada.")# Este será el archivo principal que ejecutará el sistema. A través de este script, el usuario 
# podrá interactuar con el programa para registrar clientes, crear servicios y realizar reservas. 
# También manejará las excepciones y registrará los resultados de las operaciones.
