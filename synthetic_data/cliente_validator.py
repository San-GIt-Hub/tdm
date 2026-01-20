"""
Validador determinístico de datos de clientes según contrato de datos y reglas de negocio.
"""
import re
from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anonymization.validators_ec import EcuadorValidators


class ClienteValidator:
    """Valida datos de clientes contra contrato de datos y reglas de negocio."""
    
    def __init__(self):
        self.validators_ec = EcuadorValidators()
        self.required_fields = [
            'customer_id', 'nombre', 'apellido', 'cedula', 'fecha_nacimiento',
            'email', 'direccion', 'telefono', 'fecha_creacion', 'estado_cliente'
        ]
    
    def validate_dataset(self, data):
        """
        Valida un dataset completo de clientes.
        
        Args:
            data: Lista de diccionarios con datos de clientes
            
        Returns:
            dict: Reporte de validación completo
        """
        total_records = len(data)
        errors = []
        errors_by_rule = {
            'schema': [],
            'domain': [],
            'dup': [],
            'business': []
        }
        
        # Tracking de IDs para detectar duplicados
        customer_ids_seen = {}
        
        for idx, record in enumerate(data):
            # Validar cada registro
            record_errors = self._validate_record(record, idx)
            errors.extend(record_errors)
            
            # Clasificar errores por tipo
            for error in record_errors:
                error_type = error['type']
                if error_type in errors_by_rule:
                    errors_by_rule[error_type].append(error)
            
            # Tracking de duplicados
            customer_id = record.get('customer_id')
            if customer_id:
                if customer_id in customer_ids_seen:
                    dup_error = {
                        'index': idx,
                        'customer_id': customer_id,
                        'type': 'dup',
                        'rule': 'Regla 4',
                        'field': 'customer_id',
                        'description': f'customer_id duplicado. Primera aparición en índice {customer_ids_seen[customer_id]}'
                    }
                    errors.append(dup_error)
                    errors_by_rule['dup'].append(dup_error)
                else:
                    customer_ids_seen[customer_id] = idx
        
        # Calcular métricas
        total_errors = len(errors)
        compliance_percentage = ((total_records - total_errors) / total_records * 100) if total_records > 0 else 0
        
        # Generar reporte
        report = {
            'total_registros': total_records,
            'reglas_evaluadas': [
                'Regla 1: Edad >= 18',
                'Regla 2: Si Inactivo, fecha_creacion >= 6 meses',
                'Regla 3: Email formato válido',
                'Regla 4: customer_id único',
                'Regla 5: Sin valores nulos',
                'Schema: Tipos y formatos correctos',
                'Domain: Valores en dominio permitido'
            ],
            'errores_totales': total_errors,
            'errores_por_tipo': {
                'schema': len(errors_by_rule['schema']),
                'domain': len(errors_by_rule['domain']),
                'dup': len(errors_by_rule['dup']),
                'business': len(errors_by_rule['business'])
            },
            'porcentaje_cumplimiento': round(compliance_percentage, 2),
            'muestras_de_errores': {
                'schema': errors_by_rule['schema'][:5],
                'domain': errors_by_rule['domain'][:5],
                'dup': errors_by_rule['dup'][:5],
                'business': errors_by_rule['business'][:5]
            },
            'todos_los_errores': errors
        }
        
        return report
    
    def _validate_record(self, record, index):
        """
        Valida un registro individual.
        
        Args:
            record: Diccionario con datos del cliente
            index: Índice del registro en el dataset
            
        Returns:
            list: Lista de errores encontrados
        """
        errors = []
        customer_id = record.get('customer_id', f'Unknown_{index}')
        
        # Validaciones de Schema
        errors.extend(self._validate_schema(record, index, customer_id))
        
        # Validaciones de Domain
        errors.extend(self._validate_domain(record, index, customer_id))
        
        # Validaciones de Business Rules
        errors.extend(self._validate_business_rules(record, index, customer_id))
        
        return errors
    
    def _validate_schema(self, record, index, customer_id):
        """Validaciones de esquema: campos requeridos, tipos, formatos."""
        errors = []
        
        # Regla 5: Sin valores nulos
        for field in self.required_fields:
            if field not in record or record[field] is None or str(record[field]).strip() == '':
                errors.append({
                    'index': index,
                    'customer_id': customer_id,
                    'type': 'schema',
                    'rule': 'Regla 5',
                    'field': field,
                    'description': f'Campo {field} es nulo o vacío'
                })
        
        # Validar formato de fecha_nacimiento (dd-mm-yyyy)
        if 'fecha_nacimiento' in record and record['fecha_nacimiento']:
            try:
                datetime.strptime(str(record['fecha_nacimiento']), '%d-%m-%Y')
            except ValueError:
                errors.append({
                    'index': index,
                    'customer_id': customer_id,
                    'type': 'schema',
                    'rule': 'Schema',
                    'field': 'fecha_nacimiento',
                    'description': 'Formato de fecha_nacimiento incorrecto (esperado dd-mm-yyyy)'
                })
        
        # Validar formato de fecha_creacion (dd/mm/yyyy HH:MM:SS)
        if 'fecha_creacion' in record and record['fecha_creacion']:
            try:
                datetime.strptime(str(record['fecha_creacion']), '%d/%m/%Y %H:%M:%S')
            except ValueError:
                errors.append({
                    'index': index,
                    'customer_id': customer_id,
                    'type': 'schema',
                    'rule': 'Schema',
                    'field': 'fecha_creacion',
                    'description': 'Formato de fecha_creacion incorrecto (esperado dd/mm/yyyy HH:MM:SS)'
                })
        
        # Validar que customer_id sea string alfanumérico
        if 'customer_id' in record and record['customer_id']:
            if not isinstance(record['customer_id'], str):
                errors.append({
                    'index': index,
                    'customer_id': customer_id,
                    'type': 'schema',
                    'rule': 'Schema',
                    'field': 'customer_id',
                    'description': 'customer_id debe ser string'
                })
        
        return errors
    
    def _validate_domain(self, record, index, customer_id):
        """Validaciones de dominio: valores permitidos."""
        errors = []
        
        # Regla 3: Email debe tener formato válido
        if 'email' in record and record['email']:
            email = str(record['email'])
            email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append({
                    'index': index,
                    'customer_id': customer_id,
                    'type': 'domain',
                    'rule': 'Regla 3',
                    'field': 'email',
                    'description': 'Email no tiene formato válido'
                })
        
        # Validar dominio de estado_cliente
        if 'estado_cliente' in record and record['estado_cliente']:
            estado = str(record['estado_cliente'])
            if estado not in ['Activo', 'Inactivo']:
                errors.append({
                    'index': index,
                    'customer_id': customer_id,
                    'type': 'domain',
                    'rule': 'Domain',
                    'field': 'estado_cliente',
                    'description': f'estado_cliente debe ser "Activo" o "Inactivo", recibido: {estado}'
                })
        
        # Validar formato de teléfono ecuatoriano (09XXXXXXXX)
        if 'telefono' in record and record['telefono']:
            telefono = str(record['telefono'])
            if not re.match(r'^0[0-9]{9}$', telefono):
                errors.append({
                    'index': index,
                    'customer_id': customer_id,
                    'type': 'domain',
                    'rule': 'Domain',
                    'field': 'telefono',
                    'description': 'Teléfono debe tener formato ecuatoriano (0XXXXXXXXX)'
                })
        
        # Validar cédula ecuatoriana
        if 'cedula' in record and record['cedula']:
            cedula = str(record['cedula'])
            if not self.validators_ec.validar_cedula(cedula):
                errors.append({
                    'index': index,
                    'customer_id': customer_id,
                    'type': 'domain',
                    'rule': 'Domain',
                    'field': 'cedula',
                    'description': 'Cédula no pasa validación ecuatoriana'
                })
        
        return errors
    
    def _validate_business_rules(self, record, index, customer_id):
        """Validaciones de reglas de negocio."""
        errors = []
        
        # Regla 1: Edad >= 18
        if 'fecha_nacimiento' in record and record['fecha_nacimiento']:
            try:
                fecha_nac = datetime.strptime(str(record['fecha_nacimiento']), '%d-%m-%Y')
                hoy = datetime.now()
                edad = (hoy - fecha_nac).days // 365
                
                if edad < 18:
                    errors.append({
                        'index': index,
                        'customer_id': customer_id,
                        'type': 'business',
                        'rule': 'Regla 1',
                        'field': 'fecha_nacimiento',
                        'description': f'Cliente debe tener al menos 18 años (edad actual: {edad})'
                    })
            except ValueError:
                pass  # Ya capturado en schema validation
        
        # Regla 2: Si Inactivo, fecha_creacion >= 6 meses
        if 'estado_cliente' in record and 'fecha_creacion' in record:
            estado = str(record['estado_cliente'])
            if estado == 'Inactivo' and record['fecha_creacion']:
                try:
                    fecha_creacion = datetime.strptime(str(record['fecha_creacion']), '%d/%m/%Y %H:%M:%S')
                    hoy = datetime.now()
                    meses_transcurridos = (hoy - fecha_creacion).days / 30
                    
                    if meses_transcurridos < 6:
                        errors.append({
                            'index': index,
                            'customer_id': customer_id,
                            'type': 'business',
                            'rule': 'Regla 2',
                            'field': 'fecha_creacion',
                            'description': f'Cliente Inactivo debe tener fecha_creacion >= 6 meses (actual: {meses_transcurridos:.1f} meses)'
                        })
                except ValueError:
                    pass  # Ya capturado en schema validation
        
        return errors