"""
Módulo para inyectar fallos en datos sintéticos según especificaciones del desafío.
Tipos de fallas: schema, domain, dup, business
"""
import random
from datetime import datetime, timedelta
import copy


class FaultInjector:
    """Inyecta diferentes tipos de fallos en datos para simular escenarios reales."""
    
    def __init__(self, fault_rate=0.0005, seed=None):
        """
        Inicializa el inyector de fallos.
        
        Args:
            fault_rate: Tasa de fallos a inyectar (default 0.0005 = 0.05%)
            seed: Semilla para reproducibilidad
        """
        self.fault_rate = fault_rate
        if seed:
            random.seed(seed)
        
        # Distribuir tipos de errores equitativamente
        self.error_types = ['schema', 'domain', 'dup', 'business']
    
    def inject_faults(self, data):
        """
        Inyecta todos los tipos de fallas en el dataset.
        
        Args:
            data: Lista de diccionarios con datos de clientes
            
        Returns:
            tuple: (data_con_errores, log_de_errores)
        """
        total_records = len(data)
        total_errors_to_inject = max(1, int(total_records * self.fault_rate))
        
        # Distribuir errores entre los 4 tipos
        errors_per_type = total_errors_to_inject // 4
        remaining = total_errors_to_inject % 4
        
        error_log = {
            'total_records': total_records,
            'fault_rate': self.fault_rate,
            'total_errors_injected': 0,
            'errors_by_type': {
                'schema': [],
                'domain': [],
                'dup': [],
                'business': []
            }
        }
        
        # Copiar datos para no modificar original
        faulty_data = copy.deepcopy(data)
        
        # Inyectar cada tipo de error
        schema_errors = self._inject_schema_errors(faulty_data, errors_per_type)
        error_log['errors_by_type']['schema'] = schema_errors
        
        domain_errors = self._inject_domain_errors(faulty_data, errors_per_type)
        error_log['errors_by_type']['domain'] = domain_errors
        
        dup_errors = self._inject_duplicate_errors(faulty_data, errors_per_type)
        error_log['errors_by_type']['dup'] = dup_errors
        
        business_errors = self._inject_business_errors(faulty_data, errors_per_type + remaining)
        error_log['errors_by_type']['business'] = business_errors
        
        error_log['total_errors_injected'] = (
            len(schema_errors) + len(domain_errors) + 
            len(dup_errors) + len(business_errors)
        )
        
        return faulty_data, error_log
    
    def _inject_schema_errors(self, data, count):
        """
        Inyecta errores de esquema (tipo de dato, formato, estructura).
        """
        errors = []
        indices = random.sample(range(len(data)), min(count, len(data)))
        
        for idx in indices:
            record = data[idx]
            error_type = random.choice([
                'wrong_type',
                'wrong_format',
                'null_value'
            ])
            
            if error_type == 'wrong_type':
                # Cambiar un número por string
                record['telefono'] = "NO_VALIDO"
                errors.append({
                    'index': idx,
                    'customer_id': record['customer_id'],
                    'type': 'schema',
                    'subtype': 'wrong_type',
                    'field': 'telefono',
                    'description': 'Teléfono con tipo incorrecto'
                })
            
            elif error_type == 'wrong_format':
                # Formato de fecha incorrecto
                record['fecha_nacimiento'] = '1990/13/45'  # Fecha inválida
                errors.append({
                    'index': idx,
                    'customer_id': record['customer_id'],
                    'type': 'schema',
                    'subtype': 'wrong_format',
                    'field': 'fecha_nacimiento',
                    'description': 'Formato de fecha incorrecto'
                })
            
            elif error_type == 'null_value':
                # Valor nulo donde no debería (Regla 5)
                field = random.choice(['nombre', 'email', 'cedula'])
                record[field] = None
                errors.append({
                    'index': idx,
                    'customer_id': record['customer_id'],
                    'type': 'schema',
                    'subtype': 'null_value',
                    'field': field,
                    'description': f'Campo {field} es nulo'
                })
        
        return errors
    
    def _inject_domain_errors(self, data, count):
        """
        Inyecta errores de dominio (valores fuera del conjunto permitido).
        """
        errors = []
        indices = random.sample(range(len(data)), min(count, len(data)))
        
        for idx in indices:
            record = data[idx]
            error_type = random.choice([
                'invalid_estado',
                'invalid_email_domain',
                'invalid_cedula'
            ])
            
            if error_type == 'invalid_estado':
                # Estado fuera del dominio permitido
                record['estado_cliente'] = 'SUSPENDIDO'  # No es Activo ni Inactivo
                errors.append({
                    'index': idx,
                    'customer_id': record['customer_id'],
                    'type': 'domain',
                    'subtype': 'invalid_estado',
                    'field': 'estado_cliente',
                    'description': 'Estado no pertenece al dominio {Activo, Inactivo}'
                })
            
            elif error_type == 'invalid_email_domain':
                # Email con formato inválido (Regla 3)
                record['email'] = 'correo_invalido_sin_arroba'
                errors.append({
                    'index': idx,
                    'customer_id': record['customer_id'],
                    'type': 'domain',
                    'subtype': 'invalid_email',
                    'field': 'email',
                    'description': 'Email no tiene formato válido'
                })
            
            elif error_type == 'invalid_cedula':
                # Cédula con dígito verificador incorrecto
                record['cedula'] = '1234567890'  # No pasa validación
                errors.append({
                    'index': idx,
                    'customer_id': record['customer_id'],
                    'type': 'domain',
                    'subtype': 'invalid_cedula',
                    'field': 'cedula',
                    'description': 'Cédula no pasa validación ecuatoriana'
                })
        
        return errors
    
    def _inject_duplicate_errors(self, data, count):
        """
        Inyecta errores de duplicados (violación de unicidad - Regla 4).
        """
        errors = []
        
        if len(data) < 2:
            return errors
        
        for _ in range(min(count, len(data) // 2)):
            # Seleccionar dos índices diferentes
            idx1, idx2 = random.sample(range(len(data)), 2)
            
            # Duplicar customer_id (debe ser único)
            original_id = data[idx1]['customer_id']
            data[idx2]['customer_id'] = original_id
            
            errors.append({
                'indices': [idx1, idx2],
                'customer_id': original_id,
                'type': 'dup',
                'subtype': 'duplicate_id',
                'field': 'customer_id',
                'description': f'customer_id duplicado: {original_id}'
            })
        
        return errors
    
    def _inject_business_errors(self, data, count):
        """
        Inyecta errores de reglas de negocio.
        Regla 1: Edad >= 18
        Regla 2: Si Inactivo, fecha_creacion >= 6 meses
        """
        errors = []
        indices = random.sample(range(len(data)), min(count, len(data)))
        
        for idx in indices:
            record = data[idx]
            error_type = random.choice(['edad_menor_18', 'inactivo_reciente'])
            
            if error_type == 'edad_menor_18':
                # Violación de Regla 1: Edad < 18
                hoy = datetime.now()
                fecha_menor = hoy - timedelta(days=random.randint(0, 17) * 365)
                record['fecha_nacimiento'] = fecha_menor.strftime('%d-%m-%Y')
                errors.append({
                    'index': idx,
                    'customer_id': record['customer_id'],
                    'type': 'business',
                    'subtype': 'edad_menor_18',
                    'field': 'fecha_nacimiento',
                    'description': 'Cliente menor de 18 años (Regla 1)'
                })
            
            elif error_type == 'inactivo_reciente':
                # Violación de Regla 2: Inactivo con fecha < 6 meses
                record['estado_cliente'] = 'Inactivo'
                hoy = datetime.now()
                fecha_reciente = hoy - timedelta(days=random.randint(1, 179))
                record['fecha_creacion'] = fecha_reciente.strftime('%d/%m/%Y %H:%M:%S')
                errors.append({
                    'index': idx,
                    'customer_id': record['customer_id'],
                    'type': 'business',
                    'subtype': 'inactivo_reciente',
                    'field': 'fecha_creacion',
                    'description': 'Cliente Inactivo con fecha_creacion < 6 meses (Regla 2)'
                })
        
        return errors
