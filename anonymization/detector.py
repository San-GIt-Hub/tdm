"""
Módulo para detectar tipos de datos sensibles usando patrones y reglas.
Incluye detección probabilística y validación de cédula/RUC ecuatoriano.
"""
import re
from .validators_ec import EcuadorValidators


class SensitiveDataDetector:
    """Detecta tipos específicos de datos sensibles con cálculo de probabilidad."""
    
    def __init__(self, threshold=0.90):
        """
        Inicializa el detector.
        
        Args:
            threshold: Umbral de probabilidad para considerar un campo sensible (0.0-1.0)
        """
        self.threshold = threshold
        self.patterns = self._load_patterns()
        self.validators = EcuadorValidators()
    
    def _load_patterns(self):
        """Carga patrones de expresiones regulares para detección."""
        return {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'telefono': r'\b0[0-9]{9}\b',  # Formato Ecuador: 0XXXXXXXXX
            'cedula': r'\b\d{10}\b',
            'ruc_natural': r'\b\d{13}\b',
            'ruc_empresa': r'\b\d{2}9\d{10}\b',
        }
    
    def detect(self, text, data_type=None):
        """
        Detecta datos sensibles en un texto.
        
        Args:
            text: Texto a analizar
            data_type: Tipo específico de dato a buscar (opcional)
            
        Returns:
            list: Lista de coincidencias encontradas
        """
        if data_type and data_type in self.patterns:
            return re.findall(self.patterns[data_type], text)
        
        # Buscar todos los tipos
        results = {}
        for dtype, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                results[dtype] = matches
        return results
    
    def scan_column(self, values, column_name=None):
        """
        Escanea una columna completa y calcula probabilidades de tipo de dato sensible.
        
        Args:
            values: Lista de valores de la columna
            column_name: Nombre de la columna (opcional, para hints)
            
        Returns:
            dict: Resultado con tipo detectado y probabilidad
        """
        if not values:
            return {'type': None, 'probability': 0.0, 'requires_anonymization': False}
        
        # Filtrar valores no nulos
        valid_values = [str(v) for v in values if v is not None and str(v).strip()]
        if not valid_values:
            return {'type': None, 'probability': 0.0, 'requires_anonymization': False}
        
        # Tamaño de muestra (máximo 100 registros para eficiencia)
        sample_size = min(len(valid_values), 100)
        sample = valid_values[:sample_size]
        
        # Calcular probabilidades por tipo
        type_scores = {}
        
        # Email
        email_matches = sum(1 for v in sample if re.match(self.patterns['email'], v))
        type_scores['email'] = email_matches / sample_size
        
        # Teléfono
        phone_matches = sum(1 for v in sample if re.match(self.patterns['telefono'], v))
        type_scores['telefono'] = phone_matches / sample_size
        
        # Cédula
        cedula_matches = sum(1 for v in sample 
                            if re.match(self.patterns['cedula'], v) and 
                            self.validators.validar_cedula(v))
        type_scores['cedula'] = cedula_matches / sample_size
        
        # RUC Natural
        ruc_nat_matches = sum(1 for v in sample 
                             if re.match(self.patterns['ruc_natural'], v) and 
                             self.validators.validar_ruc_natural(v))
        type_scores['ruc_natural'] = ruc_nat_matches / sample_size
        
        # RUC Empresa
        ruc_emp_matches = sum(1 for v in sample 
                             if re.match(self.patterns['ruc_empresa'], v) and 
                             self.validators.validar_ruc_empresa(v))
        type_scores['ruc_empresa'] = ruc_emp_matches / sample_size
        
        # Determinar tipo con mayor probabilidad
        detected_type = max(type_scores.items(), key=lambda x: x[1])
        
        result = {
            'type': detected_type[0] if detected_type[1] > 0 else None,
            'probability': detected_type[1],
            'all_probabilities': type_scores,
            'requires_anonymization': detected_type[1] >= self.threshold,
            'sample_size': sample_size,
            'total_records': len(valid_values),
            'threshold': self.threshold
        }
        
        return result
    
    def scan_dataset(self, data, column_names=None):
        """
        Escanea un dataset completo (lista de diccionarios).
        
        Args:
            data: Lista de diccionarios con los datos
            column_names: Lista de nombres de columnas a escanear (None = todas)
            
        Returns:
            dict: Resultados de escaneo por columna
        """
        if not data:
            return {}
        
        # Obtener nombres de columnas
        if column_names is None:
            column_names = list(data[0].keys()) if data else []
        
        results = {}
        for col in column_names:
            values = [record.get(col) for record in data]
            results[col] = self.scan_column(values, col)
        
        return results
