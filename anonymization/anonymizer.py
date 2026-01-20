"""
Módulo para anonimizar datos sensibles con anonimización determinística.
"""
from faker import Faker
import hashlib
import random
from .validators_ec import EcuadorValidators


class DataAnonymizer:
    """Anonimiza datos sensibles aplicando diferentes técnicas de forma determinística."""
    
    def __init__(self, locale='es_ES', master_seed=None):
        """
        Inicializa el anonimizador.
        
        Args:
            locale: Localización para datos sintéticos
            master_seed: Semilla maestra para determinismo
        """
        self.locale = locale
        self.master_seed = master_seed
        self.faker = Faker(locale)
        self.validators = EcuadorValidators()
    
    def _get_seed_from_value(self, value, salt=''):
        """
        Genera una semilla determinística basada en un valor.
        
        Args:
            value: Valor original
            salt: Salt adicional para diferenciación
            
        Returns:
            int: Semilla generada
        """
        combined = f"{self.master_seed}_{value}_{salt}"
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        # Usar los primeros 8 bytes del hash como semilla
        return int.from_bytes(hash_obj.digest()[:8], byteorder='big')
    
    def mask(self, value, mask_char='*', visible_chars=4):
        """
        Enmascara un valor dejando visible solo algunos caracteres.
        
        Args:
            value: Valor a enmascarar
            mask_char: Carácter para enmascarar
            visible_chars: Número de caracteres visibles al final
            
        Returns:
            str: Valor enmascarado
        """
        if not value:
            return value
        value_str = str(value)
        if len(value_str) <= visible_chars:
            return mask_char * len(value_str)
        return mask_char * (len(value_str) - visible_chars) + value_str[-visible_chars:]
    
    def hash(self, value, algorithm='sha256'):
        """
        Aplica hash a un valor.
        
        Args:
            value: Valor a hashear
            algorithm: Algoritmo de hash a utilizar
            
        Returns:
            str: Hash del valor
        """
        if not value:
            return value
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(str(value).encode('utf-8'))
        return hash_obj.hexdigest()
    
    def pseudonymize(self, value, data_type='name'):
        """
        Reemplaza un valor con datos falsos pero realistas de forma determinística.
        
        Args:
            value: Valor a pseudonimizar
            data_type: Tipo de dato (name, email, telefono, cedula, ruc_natural, ruc_empresa)
            
        Returns:
            str: Valor pseudonimizado
        """
        if not value:
            return value
        
        # Generar semilla basada en el valor original
        seed = self._get_seed_from_value(value, data_type)
        
        # Crear un generador random determinístico
        rand_gen = random.Random(seed)
        Faker.seed(seed)
        faker_instance = Faker(self.locale)
        
        # Generar valor basado en el tipo
        if data_type == 'name':
            return faker_instance.name()
        elif data_type == 'email':
            # Generar email real, no nombre
            return faker_instance.email()
        elif data_type == 'telefono':
            # Generar teléfono ecuatoriano: 09XXXXXXXX
            telefono = '09' + ''.join([str(rand_gen.randint(0, 9)) for _ in range(8)])
            return telefono
        elif data_type == 'cedula':
            # Generar cédula válida
            provincia = rand_gen.randint(1, 24)
            return self.validators.generar_cedula_valida(provincia, rand_gen)
        elif data_type == 'ruc_natural':
            # Generar RUC natural válido
            provincia = rand_gen.randint(1, 24)
            return self.validators.generar_ruc_natural(provincia, rand_gen)
        elif data_type == 'ruc_empresa':
            # Generar RUC empresa válido
            provincia = rand_gen.randint(1, 24)
            return self.validators.generar_ruc_empresa(provincia, rand_gen)
        elif data_type == 'address':
            return faker_instance.address()
        elif data_type == 'company':
            return faker_instance.company()
        else:
            return faker_instance.name()
    
    def generalize(self, value, precision=10):
        """
        Generaliza un valor numérico reduciéndolo a un rango.
        
        Args:
            value: Valor numérico a generalizar
            precision: Precisión del rango
            
        Returns:
            str: Rango generalizado
        """
        if not isinstance(value, (int, float)):
            return value
        lower = (value // precision) * precision
        upper = lower + precision
        return f"{lower}-{upper}"
    
    def anonymize_dataset(self, data, rules_engine):
        """
        Anonimiza un dataset completo aplicando las reglas.
        
        Args:
            data: Lista de diccionarios con datos
            rules_engine: Motor de reglas de anonimización
            
        Returns:
            list: Dataset anonimizado
        """
        anonymized_data = []
        for record in data:
            anonymized_record = rules_engine.apply_rules(record, self)
            anonymized_data.append(anonymized_record)
        return anonymized_data
