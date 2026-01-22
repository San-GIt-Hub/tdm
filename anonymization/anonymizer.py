"""
Módulo para anonimizar datos sensibles con anonimización determinística.
"""
from faker import Faker
import hashlib
import random
from .validators_ec import EcuadorValidators
import json
import csv
import os
from datetime import datetime
from pathlib import Path


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

    def _ensure_outdir(self, out_dir):
        """
        Asegura la existencia de un directorio de salida.

        Args:
            out_dir: Directorio de salida

        Returns:
            Path: Directorio de salida
        """
        if out_dir is None:
            out_dir = Path(r"c:\PROYECTOS\tdm_anonimizacion\data\output")
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def save_json(self, data, out_path):
        """
        Guarda una lista de dicts en JSON (utf-8).

        Args:
            data: Lista de diccionarios
            out_path: Ruta de salida

        Returns:
            str: Ruta de salida
        """
        out_path = Path(out_path)
        with out_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(out_path)

    def save_csv(self, data, out_path):
        """
        Guarda una lista de dicts en CSV. Calcula cabeceras por unión de keys.

        Args:
            data: Lista de diccionarios
            out_path: Ruta de salida

        Returns:
            str: Ruta de salida
        """
        out_path = Path(out_path)
        if not data:
            # crear archivo vacío con cabecera vacía
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text("")
            return str(out_path)
        # unir claves de todos los registros para definir columnas
        fieldnames = []
        for row in data:
            for k in row.keys():
                if k not in fieldnames:
                    fieldnames.append(k)
        with out_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        return str(out_path)

    def save_comparison(self, originals, anonymized, out_dir=None, formats=('json','csv'), prefix='anonimizado'):
        """
        Guarda originales y anonimizado en archivos con timestamp y seed.
        Devuelve lista de rutas creadas.
        """
        out_dir = self._ensure_outdir(out_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        seed_part = str(self.master_seed) if self.master_seed is not None else "noseed"
        
        created = []
        # archivos para originales
        base_orig = f"{prefix}_originals_{timestamp}_seed{seed_part}"
        base_anon = f"{prefix}_anonymized_{timestamp}_seed{seed_part}"
        
        if 'json' in formats:
            p_orig = out_dir / (base_orig + ".json")
            p_anon = out_dir / (base_anon + ".json")
            self.save_json(originals, p_orig)
            self.save_json(anonymized, p_anon)
            created += [str(p_orig), str(p_anon)]
        if 'csv' in formats:
            p_orig = out_dir / (base_orig + ".csv")
            p_anon = out_dir / (base_anon + ".csv")
            self.save_csv(originals, p_orig)
            self.save_csv(anonymized, p_anon)
            created += [str(p_orig), str(p_anon)]
        
        return created
