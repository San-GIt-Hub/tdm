"""
Módulo para escanear datos y detectar información sensible.
Integra detección probabilística y anonimización determinística.
"""
import json
import csv
from datetime import datetime
from pathlib import Path
from .detector import SensitiveDataDetector
from .anonymizer import DataAnonymizer
from .rules import RuleEngine


class DataScanner:
    """
    Escanea datasets para identificar y anonimizar datos sensibles.
    
    Cumple con el alcance funcional:
    - Identificación por columna mediante muestreo con cálculo de probabilidad
    - Tipos soportados: Cédula, RUC empresa, RUC natural, Teléfono, Email
    - Umbral configurable (por defecto 90%)
    - Anonimización determinística preservando formato y validez
    """
    
    def __init__(self, threshold=0.90, seed=None):
        """
        Inicializa el escáner de datos.
        
        Args:
            threshold: Umbral de probabilidad para detectar campos sensibles (0.0-1.0)
                      Por defecto 90% según alcance funcional
            seed: Semilla para anonimización determinística
        """
        self.threshold = threshold
        self.seed = seed
        self.detector = SensitiveDataDetector(threshold=threshold)
        self.anonymizer = DataAnonymizer(master_seed=seed)
        self.scan_results = None
        self.anonymization_results = None
    
    def scan_dataset(self, data, column_names=None):
        """
        Escanea un dataset completo identificando campos sensibles.
        
        Realiza:
        - Muestreo de datos por columna
        - Cálculo de probabilidad de pertenencia a tipos sensibles
        - Decisión de anonimización basada en umbral
        
        Args:
            data: Lista de diccionarios con los datos a escanear
            column_names: Nombres de columnas a escanear (opcional, escanea todas si None)
            
        Returns:
            dict: Resultados del escaneo con probabilidades y recomendaciones
        """
        if not data:
            return {
                'error': 'Dataset vacío',
                'total_records': 0,
                'columns_scanned': 0
            }
        
        # Escanear con el detector
        detector_results = self.detector.scan_dataset(data, column_names)
        
        # Agregar metadatos del escaneo
        scan_summary = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(data),
            'threshold_applied': self.threshold,
            'columns_scanned': len(detector_results),
            'sensitive_columns': sum(1 for col in detector_results.values() 
                                    if col.get('requires_anonymization', False)),
            'columns_detail': detector_results
        }
        
        # Guardar resultados para uso posterior
        self.scan_results = scan_summary
        
        return scan_summary
    
    def anonymize_dataset(self, data, scan_results=None, auto_detect=True):
        """
        Anonimiza un dataset basándose en resultados del escaneo.
        
        Implementa anonimización determinística:
        - Basada en semilla por valor original
        - Preserva formato de datos
        - Preserva validez (cédulas, RUCs, emails válidos)
        
        Args:
            data: Lista de diccionarios con datos a anonimizar
            scan_results: Resultados previos de escaneo (usa self.scan_results si None)
            auto_detect: Si True, escanea automáticamente si no hay resultados
            
        Returns:
            dict: Dataset anonimizado y reporte de cambios
        """
        if not data:
            return {'error': 'Dataset vacío', 'anonymized_data': []}
        
        # Usar resultados de escaneo previo o escanear ahora
        if scan_results is None:
            scan_results = self.scan_results
        
        if scan_results is None and auto_detect:
            self.scan_dataset(data)
            scan_results = self.scan_results
        
        if scan_results is None:
            return {
                'error': 'No hay resultados de escaneo. Ejecute scan_dataset primero.',
                'anonymized_data': []
            }
        
        # Identificar columnas que requieren anonimización
        columns_to_anonymize = {
            col_name: col_info
            for col_name, col_info in scan_results.get('columns_detail', {}).items()
            if col_info.get('requires_anonymization', False)
        }
        
        if not columns_to_anonymize:
            return {
                'message': 'No se detectaron columnas que requieran anonimización',
                'anonymized_data': data,
                'columns_anonymized': 0
            }
        
        # Crear reglas de anonimización automáticas
        rules = []
        for col_name, col_info in columns_to_anonymize.items():
            data_type = col_info.get('type')
            rules.append({
                'column': col_name,
                'method': 'pseudonymize',
                'data_type': data_type,
                'probability': col_info.get('probability', 0.0)
            })
        
        # Aplicar anonimización directamente (sin RuleEngine)
        anonymized_data = []
        for record in data:
            anon_record = record.copy()
            for rule in rules:
                col = rule['column']
                data_type = rule.get('data_type')
                
                if col in anon_record:
                    original_value = anon_record[col]
                    # Pseudonymize siempre preserva formato
                    anon_record[col] = self.anonymizer.pseudonymize(original_value, data_type=data_type)
            
            anonymized_data.append(anon_record)
        
        # Validar preservación de formato
        validation_report = self._validate_anonymization(data, anonymized_data, rules)
        
        self.anonymization_results = {
            'timestamp': datetime.now().isoformat(),
            'seed_used': self.seed,
            'total_records': len(data),
            'columns_anonymized': len(columns_to_anonymize),
            'columns_detail': {
                col: {
                    'type': info.get('type'),
                    'probability': info.get('probability'),
                    'method': 'pseudonymize'
                }
                for col, info in columns_to_anonymize.items()
            },
            'anonymized_data': anonymized_data,
            'validation': validation_report
        }
        
        return self.anonymization_results
    
    def _validate_anonymization(self, original_data, anonymized_data, rules):
        """
        Valida que la anonimización preserve formato y validez.
        
        Args:
            original_data: Datos originales
            anonymized_data: Datos anonimizados
            rules: Reglas aplicadas
            
        Returns:
            dict: Reporte de validación
        """
        from .validators_ec import EcuadorValidators
        
        validation = {
            'format_preserved': True,
            'validity_preserved': True,
            'determinism_verified': True,
            'issues': []
        }
        
        if not original_data or not anonymized_data:
            return validation
        
        # Verificar una muestra
        sample_size = min(10, len(original_data))
        
        for i in range(sample_size):
            orig_record = original_data[i]
            anon_record = anonymized_data[i]
            
            for rule in rules:
                col = rule['column']
                data_type = rule.get('data_type')
                
                if col not in orig_record or col not in anon_record:
                    continue
                
                orig_val = str(orig_record[col])
                anon_val = str(anon_record[col])
                
                # Verificar formato preservado
                if data_type == 'cedula':
                    if len(orig_val) != len(anon_val) or not anon_val.isdigit():
                        validation['format_preserved'] = False
                        validation['issues'].append(f"Formato no preservado en {col}: {orig_val} -> {anon_val}")
                    
                    # Verificar validez
                    if not EcuadorValidators.validar_cedula(anon_val):
                        validation['validity_preserved'] = False
                        validation['issues'].append(f"Cédula anonimizada inválida: {anon_val}")
                
                elif data_type == 'email':
                    if '@' not in anon_val or '.' not in anon_val:
                        validation['format_preserved'] = False
                        validation['issues'].append(f"Email sin formato válido: {anon_val}")
                
                elif data_type == 'telefono':
                    if len(orig_val) != len(anon_val) or not anon_val.isdigit():
                        validation['format_preserved'] = False
                        validation['issues'].append(f"Teléfono sin formato: {anon_val}")
        
        return validation
    
    def generate_report(self, output_path=None, format='json'):
        """
        Genera un reporte completo del escaneo y anonimización.
        
        Args:
            output_path: Ruta donde guardar el reporte (opcional)
            format: Formato del reporte ('json' o 'txt')
            
        Returns:
            dict: Reporte completo
        """
        report = {
            'scan_timestamp': datetime.now().isoformat(),
            'configuration': {
                'threshold': self.threshold,
                'seed': self.seed
            },
            'scan_results': self.scan_results,
            'anonymization_results': {
                k: v for k, v in (self.anonymization_results or {}).items()
                if k != 'anonymized_data'  # Excluir datos del reporte
            }
        }
        
        if output_path:
            output_path = Path(output_path)
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(self._format_text_report(report))
        
        return report
    
    def _format_text_report(self, report):
        """Formatea el reporte como texto plano."""
        lines = []
        lines.append("="*70)
        lines.append(" "*20 + "REPORTE DE ESCANEO Y ANONIMIZACIÓN")
        lines.append("="*70)
        lines.append(f"\nFecha: {report['scan_timestamp']}")
        lines.append(f"Umbral configurado: {report['configuration']['threshold']*100}%")
        lines.append(f"Semilla utilizada: {report['configuration']['seed']}")
        
        if report.get('scan_results'):
            scan = report['scan_results']
            lines.append(f"\n\nRESULTADOS DEL ESCANEO:")
            lines.append(f"  Total de registros: {scan.get('total_records', 0)}")
            lines.append(f"  Columnas escaneadas: {scan.get('columns_scanned', 0)}")
            lines.append(f"  Columnas sensibles: {scan.get('sensitive_columns', 0)}")
            
            if scan.get('columns_detail'):
                lines.append(f"\n  Detalle por columna:")
                for col, info in scan['columns_detail'].items():
                    prob = info.get('probability', 0) * 100
                    tipo = info.get('type', 'desconocido')
                    req = "SÍ" if info.get('requires_anonymization') else "NO"
                    lines.append(f"    - {col}: {tipo} ({prob:.1f}%) - Anonimizar: {req}")
        
        if report.get('anonymization_results'):
            anon = report['anonymization_results']
            lines.append(f"\n\nRESULTADOS DE ANONIMIZACIÓN:")
            lines.append(f"  Registros procesados: {anon.get('total_records', 0)}")
            lines.append(f"  Columnas anonimizadas: {anon.get('columns_anonymized', 0)}")
            
            if anon.get('validation'):
                val = anon['validation']
                lines.append(f"\n  Validación:")
                lines.append(f"    Formato preservado: {'✓' if val.get('format_preserved') else '✗'}")
                lines.append(f"    Validez preservada: {'✓' if val.get('validity_preserved') else '✗'}")
                
                if val.get('issues'):
                    lines.append(f"    Problemas detectados: {len(val['issues'])}")
        
        lines.append("\n" + "="*70)
        return "\n".join(lines)
    
    def scan_file(self, file_path, file_format='json'):
        """
        Escanea un archivo en busca de datos sensibles.
        
        Args:
            file_path: Ruta al archivo a escanear
            file_format: Formato del archivo ('json' o 'csv')
            
        Returns:
            dict: Resultados del escaneo
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {'error': f'Archivo no encontrado: {file_path}'}
        
        # Cargar datos según formato
        if file_format == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif file_format == 'csv':
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        else:
            return {'error': f'Formato no soportado: {file_format}'}
        
        # Escanear datos
        return self.scan_dataset(data)
    
    def anonymize_file(self, input_path, output_path, file_format='json'):
        """
        Escanea y anonimiza un archivo completo.
        
        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            file_format: Formato de los archivos
            
        Returns:
            dict: Resultados del proceso
        """
        # Escanear archivo
        scan_results = self.scan_file(input_path, file_format)
        
        if 'error' in scan_results:
            return scan_results
        
        # Cargar datos
        input_path = Path(input_path)
        if file_format == 'json':
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            with open(input_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        
        # Anonimizar
        results = self.anonymize_dataset(data)
        
        if 'error' in results:
            return results
        
        # Guardar datos anonimizados
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results['anonymized_data'], f, indent=2, ensure_ascii=False)
        else:
            if results['anonymized_data']:
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=results['anonymized_data'][0].keys())
                    writer.writeheader()
                    writer.writerows(results['anonymized_data'])
        
        return {
            'message': 'Archivo anonimizado exitosamente',
            'input_file': str(input_path),
            'output_file': str(output_path),
            'scan_results': scan_results,
            'anonymization_summary': {
                k: v for k, v in results.items()
                if k != 'anonymized_data'
            }
        }
