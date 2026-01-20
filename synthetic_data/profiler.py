"""
Módulo para perfilar y analizar conjuntos de datos.
"""
from collections import Counter
import statistics


class DataProfiler:
    """Analiza y crea perfiles de conjuntos de datos."""
    
    def __init__(self):
        self.profile = {}
    
    def profile_dataset(self, data):
        """
        Crea un perfil completo de un conjunto de datos.
        
        Args:
            data: Lista de diccionarios con datos
            
        Returns:
            dict: Perfil del conjunto de datos
        """
        if not data:
            return {'error': 'No data provided'}
        
        profile = {
            'record_count': len(data),
            'fields': {},
        }
        
        # Obtener todos los campos
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        # Perfilar cada campo
        for field in all_fields:
            profile['fields'][field] = self.profile_field(data, field)
        
        return profile
    
    def profile_field(self, data, field):
        """
        Crea un perfil de un campo específico.
        
        Args:
            data: Lista de diccionarios con datos
            field: Nombre del campo a perfilar
            
        Returns:
            dict: Perfil del campo
        """
        values = [record.get(field) for record in data if field in record]
        non_null_values = [v for v in values if v is not None]
        
        field_profile = {
            'total_count': len(values),
            'non_null_count': len(non_null_values),
            'null_count': len(values) - len(non_null_values),
            'null_percentage': ((len(values) - len(non_null_values)) / len(values) * 100) if values else 0,
        }
        
        if non_null_values:
            # Determinar tipo de dato
            sample_value = non_null_values[0]
            if isinstance(sample_value, bool):
                field_profile['data_type'] = 'boolean'
                field_profile['distribution'] = dict(Counter(non_null_values))
            elif isinstance(sample_value, int):
                field_profile['data_type'] = 'integer'
                field_profile.update(self._profile_numeric(non_null_values))
            elif isinstance(sample_value, float):
                field_profile['data_type'] = 'float'
                field_profile.update(self._profile_numeric(non_null_values))
            elif isinstance(sample_value, str):
                field_profile['data_type'] = 'string'
                field_profile.update(self._profile_string(non_null_values))
            else:
                field_profile['data_type'] = 'other'
        
        return field_profile
    
    def _profile_numeric(self, values):
        """Perfila campos numéricos."""
        return {
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
        }
    
    def _profile_string(self, values):
        """Perfila campos de texto."""
        lengths = [len(str(v)) for v in values]
        counter = Counter(values)
        
        return {
            'unique_count': len(counter),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'avg_length': statistics.mean(lengths),
            'most_common': counter.most_common(5),
        }
    
    def compare_profiles(self, profile1, profile2):
        """
        Compara dos perfiles de datos.
        
        Args:
            profile1: Primer perfil
            profile2: Segundo perfil
            
        Returns:
            dict: Comparación de perfiles
        """
        comparison = {
            'record_count_diff': profile2['record_count'] - profile1['record_count'],
            'field_differences': {},
        }
        
        # Comparar campos
        fields1 = set(profile1['fields'].keys())
        fields2 = set(profile2['fields'].keys())
        
        comparison['new_fields'] = list(fields2 - fields1)
        comparison['removed_fields'] = list(fields1 - fields2)
        comparison['common_fields'] = list(fields1 & fields2)
        
        return comparison
