"""
Módulo para validar la calidad de datos sintéticos.
"""
import re
from collections import Counter


class DataValidator:
    """Valida la calidad y consistencia de datos sintéticos."""
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_completeness(self, data, required_fields):
        """
        Valida que todos los campos requeridos estén presentes.
        
        Args:
            data: Lista de diccionarios con datos
            required_fields: Lista de campos requeridos
            
        Returns:
            dict: Resultados de validación
        """
        missing_counts = {field: 0 for field in required_fields}
        total_records = len(data)
        
        for record in data:
            for field in required_fields:
                if field not in record or record[field] is None or record[field] == '':
                    missing_counts[field] += 1
        
        completeness = {
            field: (total_records - count) / total_records * 100
            for field, count in missing_counts.items()
        }
        
        return {
            'metric': 'completeness',
            'total_records': total_records,
            'missing_counts': missing_counts,
            'completeness_percentage': completeness,
        }
    
    def validate_uniqueness(self, data, unique_fields):
        """
        Valida la unicidad de campos que deberían ser únicos.
        
        Args:
            data: Lista de diccionarios con datos
            unique_fields: Lista de campos que deben ser únicos
            
        Returns:
            dict: Resultados de validación
        """
        results = {}
        
        for field in unique_fields:
            values = [record.get(field) for record in data if record.get(field) is not None]
            total = len(values)
            unique = len(set(values))
            duplicates = total - unique
            
            results[field] = {
                'total_values': total,
                'unique_values': unique,
                'duplicate_count': duplicates,
                'uniqueness_percentage': (unique / total * 100) if total > 0 else 0,
            }
        
        return {
            'metric': 'uniqueness',
            'results': results,
        }
    
    def validate_format(self, data, field, pattern):
        """
        Valida que un campo cumpla con un formato específico.
        
        Args:
            data: Lista de diccionarios con datos
            field: Nombre del campo a validar
            pattern: Expresión regular del formato esperado
            
        Returns:
            dict: Resultados de validación
        """
        compiled_pattern = re.compile(pattern)
        total = 0
        valid = 0
        invalid_values = []
        
        for record in data:
            if field in record and record[field] is not None:
                total += 1
                value = str(record[field])
                if compiled_pattern.match(value):
                    valid += 1
                else:
                    invalid_values.append(value)
        
        return {
            'metric': 'format_validation',
            'field': field,
            'pattern': pattern,
            'total_values': total,
            'valid_count': valid,
            'invalid_count': total - valid,
            'validity_percentage': (valid / total * 100) if total > 0 else 0,
            'sample_invalid': invalid_values[:5],
        }
    
    def validate_distribution(self, data, field):
        """
        Analiza la distribución de valores en un campo.
        
        Args:
            data: Lista de diccionarios con datos
            field: Nombre del campo a analizar
            
        Returns:
            dict: Resultados del análisis
        """
        values = [record.get(field) for record in data if record.get(field) is not None]
        counter = Counter(values)
        
        return {
            'metric': 'distribution',
            'field': field,
            'total_values': len(values),
            'unique_values': len(counter),
            'most_common': counter.most_common(10),
        }
    
    def generate_report(self):
        """
        Genera un reporte completo de validación.
        
        Returns:
            dict: Reporte de validación
        """
        return {
            'validation_results': self.validation_results,
            'summary': {
                'total_validations': len(self.validation_results),
            }
        }
