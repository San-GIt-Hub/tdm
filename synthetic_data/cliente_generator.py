"""
Generador de clientes sintéticos según especificaciones del desafío.

Campos: customer_id, nombre, apellido, cedula, fecha_nacimiento, email, 
        direccion, telefono, fecha_creacion, estado_cliente
"""
from faker import Faker
import random
from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anonymization.validators_ec import EcuadorValidators


class ClienteGenerator:
    """Genera datos sintéticos de clientes según especificaciones."""
    
    def __init__(self, locale='es_ES', seed=None):
        """
        Inicializa el generador.
        
        Args:
            locale: Localización para datos generados
            seed: Semilla para reproducibilidad
        """
        self.locale = locale
        self.seed = seed
        self.faker = Faker(locale)
        self.validators = EcuadorValidators()
        
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)
    
    def _generate_customer_id(self, index):
        """
        Genera un customer_id único autosecuencial.
        
        Args:
            index: Índice del cliente
            
        Returns:
            str: ID del cliente (ej: Cus001)
        """
        return f"Cus{index:03d}"
    
    def _generate_fecha_nacimiento(self):
        """
        Genera una fecha de nacimiento para persona >= 18 años.
        
        Returns:
            str: Fecha en formato dd-mm-yyyy
        """
        # Edad entre 18 y 90 años
        edad = random.randint(18, 90)
        hoy = datetime.now()
        fecha_nacimiento = hoy - timedelta(days=edad * 365 + random.randint(0, 364))
        return fecha_nacimiento.strftime('%d-%m-%Y')
    
    def _generate_email(self, nombre, apellido):
        """
        Genera un email coherente con nombre y apellido.
        
        Args:
            nombre: Nombre del cliente
            apellido: Apellido del cliente
            
        Returns:
            str: Email generado
        """
        import unicodedata
        
        def remove_accents(text):
            """Elimina acentos y caracteres especiales."""
            nfkd = unicodedata.normalize('NFKD', text)
            return ''.join([c for c in nfkd if not unicodedata.combining(c)])
        
        dominios = ['test.com', 'example.com', 'demo.ec', 'prueba.com']
        nombre_clean = remove_accents(nombre.lower()).replace(' ', '.')
        apellido_clean = remove_accents(apellido.lower()).replace(' ', '.')
        dominio = random.choice(dominios)
        
        # Diferentes formatos
        formatos = [
            f"{nombre_clean}.{apellido_clean}@{dominio}",
            f"{nombre_clean[0]}.{apellido_clean}@{dominio}",
            f"{nombre_clean}{apellido_clean[0]}@{dominio}",
        ]
        
        return random.choice(formatos)
    
    def _generate_telefono(self):
        """
        Genera un teléfono ecuatoriano sintético.
        
        Returns:
            str: Teléfono en formato 09XXXXXXXX
        """
        return '09' + ''.join([str(random.randint(0, 9)) for _ in range(8)])
    
    def _generate_estado_cliente(self):
        """
        Genera un estado de cliente (Activo/Inactivo).
        
        Returns:
            str: 'Activo' o 'Inactivo'
        """
        # 80% activos, 20% inactivos
        return 'Activo' if random.random() < 0.8 else 'Inactivo'
    
    def _generate_fecha_creacion(self, estado):
        """
        Genera fecha de creación según reglas de negocio.
        
        Args:
            estado: Estado del cliente ('Activo' o 'Inactivo')
            
        Returns:
            str: Fecha y hora en formato dd/mm/yyyy HH:MM:SS
        """
        hoy = datetime.now()
        
        if estado == 'Inactivo':
            # Debe ser >= 6 meses atrás
            meses_atras = random.randint(6, 36)
            fecha = hoy - timedelta(days=meses_atras * 30 + random.randint(0, 30))
        else:
            # Puede ser cualquier fecha en los últimos 5 años
            dias_atras = random.randint(0, 365 * 5)
            fecha = hoy - timedelta(days=dias_atras)
        
        return fecha.strftime('%d/%m/%Y %H:%M:%S')
    
    def generate_cliente(self, index=1):
        """
        Genera un cliente sintético completo.
        
        Args:
            index: Índice del cliente para customer_id
            
        Returns:
            dict: Datos del cliente
        """
        nombre = self.faker.first_name()
        apellido = self.faker.last_name()
        cedula = self.validators.generar_cedula_valida(
            provincia=random.randint(1, 24),
            random_gen=random
        )
        fecha_nacimiento = self._generate_fecha_nacimiento()
        email = self._generate_email(nombre, apellido)
        direccion = self.faker.address().replace('\n', ', ')
        telefono = self._generate_telefono()
        estado = self._generate_estado_cliente()
        fecha_creacion = self._generate_fecha_creacion(estado)
        
        return {
            'customer_id': self._generate_customer_id(index),
            'nombre': nombre,
            'apellido': apellido,
            'cedula': cedula,
            'fecha_nacimiento': fecha_nacimiento,
            'email': email,
            'direccion': direccion,
            'telefono': telefono,
            'fecha_creacion': fecha_creacion,
            'estado_cliente': estado
        }
    
    def generate_clientes(self, count=100):
        """
        Genera múltiples clientes.
        
        Args:
            count: Número de clientes a generar
            
        Returns:
            list: Lista de diccionarios con datos de clientes
        """
        clientes = []
        for i in range(1, count + 1):
            cliente = self.generate_cliente(index=i)
            clientes.append(cliente)
        return clientes
