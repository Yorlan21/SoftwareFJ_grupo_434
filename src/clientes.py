# Este archivo contendrá la clase Cliente, la cual gestionará la validación de los datos 
# personales de los clientes. Los datos como nombre, email y teléfono estarán encapsulados y validados 
# para asegurar que la información ingresada sea correcta.

from excepciones import DatosInvalidosError  # Traemos la excepción para manejar cuando los datos no sean válidos

# Clase Cliente: Aquí es donde guardamos y validamos la información del cliente

class Cliente:
    def __init__(self, nombre, email, telefono):  # Guardamos los datos que el cliente nos da
        self.nombre = nombre  # Guardamos el nombre del cliente
        self.email = email  # Guardamos el email del cliente
        self.telefono = telefono  # Guardamos el teléfono del cliente

    def validar(self):  # Validamos que el cliente tenga todos los datos importantes
        if not self.nombre or not self.email or not self.telefono:  # Si falta algún dato
            raise DatosInvalidosError("Faltan datos del cliente.")  # Lanzamos un error para decir que algo falta
# Yorlan Rivera 
 # Validación para asegurar que el email no esté vacío
        if not self.__email:
            raise DatosInvalidosError("El email del cliente no puede estar vacío.")

        # Validación de formato de email
        if "@" not in self.__email or "." not in self.__email:
            raise DatosInvalidosError("El email del cliente no tiene un formato válido.")

        # Validación para asegurar que el teléfono no esté vacío
        if not self.__telefono:
            raise DatosInvalidosError("El teléfono del cliente no puede estar vacío.")

        # Validación para asegurar que el teléfono contiene solo números
        if not self.__telefono.isdigit():
            raise DatosInvalidosError("El teléfono solo debe contener números.")

        # Validación para asegurar que el teléfono tenga al menos 7 dígitos
        if len(self.__telefono) < 7:
            raise DatosInvalidosError("El teléfono debe tener mínimo 7 dígitos.")

    # Métodos getters para acceder a los datos privados
    def get_nombre(self):
        return self.__nombre

    def get_email(self):
        return self.__email

    def get_telefono(self):
        return self.__telefono

    # Método para mostrar la información del cliente
    def mostrar_info(self):
        return f"Cliente: {self.__nombre} | Email: {self.__email} | Teléfono: {self.__telefono}"
        
#Comentario explicativo:
# En Cliente, guardamos los datos que un cliente nos da (como su nombre, email y teléfono).
# El método validar se asegura de que no falte nada importante y si falta algún dato, lanza un error para avisar.
