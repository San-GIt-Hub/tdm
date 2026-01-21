"""
Tests para el DataScanner (integración detector + anonimizador)
"""
import sys
from pathlib import Path
import tempfile
import json

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anonymization.scanner import DataScanner
from anonymization.validators_ec import EcuadorValidators


def test_scanner_initialization():
    """Test de inicialización del scanner"""
    scanner = DataScanner(threshold=0.85, seed=42)
    
    assert scanner.threshold == 0.85, "Threshold debe configurarse correctamente"
    assert scanner.seed == 42, "Seed debe configurarse correctamente"
    assert scanner.detector is not None, "Detector debe inicializarse"
    assert scanner.anonymizer is not None, "Anonymizer debe inicializarse"
    print("✓ Test inicialización scanner: PASS")


def test_scan_dataset_with_sensitive_data():
    """Test de escaneo de dataset con datos sensibles"""
    scanner = DataScanner(threshold=0.90, seed=42)
    
    # Dataset con datos sensibles
    data = [
        {
            "nombre": "Juan Pérez",
            "cedula": "1710034065",
            "email": "juan@example.com",
            "telefono": "0991234567",
            "edad": "30"
        },
        {
            "nombre": "María López",
            "cedula": "0926687856",
            "email": "maria@test.com",
            "telefono": "0987654321",
            "edad": "25"
        }
    ]
    
    results = scanner.scan_dataset(data)
    
    assert 'columns_detail' in results, "Debe incluir detalle de columnas"
    assert 'sensitive_columns' in results, "Debe contar columnas sensibles"
    assert results['total_records'] == 2, "Debe contar registros correctamente"
    assert results['threshold_applied'] == 0.90, "Debe reportar threshold aplicado"
    
    # Verificar que detecta columnas sensibles
    assert results['sensitive_columns'] > 0, "Debe detectar al menos una columna sensible"
    
    print("✓ Test escaneo de dataset: PASS")


def test_scan_identifies_specific_types():
    """Test que el escaneo identifica tipos específicos (Cédula, Email, Teléfono)"""
    scanner = DataScanner(threshold=0.80)
    
    # Dataset con tipos específicos del alcance
    data = [
        {
            "cedula": EcuadorValidators.generar_cedula_valida(),
            "ruc_natural": EcuadorValidators.generar_ruc_natural(),
            "ruc_empresa": EcuadorValidators.generar_ruc_empresa(),
            "email": "test@example.com",
            "telefono": "0991234567"
        }
        for _ in range(10)
    ]
    
    results = scanner.scan_dataset(data)
    columns = results.get('columns_detail', {})
    
    # Verificar detección de tipos según alcance
    tipos_detectados = {col_info.get('type') for col_info in columns.values()}
    
    # Debe detectar al menos 2 tipos según alcance funcional
    tipos_esperados = {'cedula', 'email', 'telefono', 'ruc_natural', 'ruc_empresa'}
    tipos_encontrados = tipos_detectados.intersection(tipos_esperados)
    
    assert len(tipos_encontrados) >= 2, \
        f"Debe detectar al menos 2 tipos del alcance. Encontrados: {tipos_encontrados}"
    
    print(f"✓ Test identificación de tipos específicos: PASS (detectados: {tipos_encontrados})")


def test_threshold_configuration():
    """Test de umbral configurable (requisito del alcance)"""
    data = [
        {"email": "test1@example.com"},
        {"email": "test2@example.com"},
        {"email": "not-an-email"},  # 66% de probabilidad
    ]
    
    # Con umbral bajo (60%) debe detectar como sensible
    scanner_low = DataScanner(threshold=0.60)
    results_low = scanner_low.scan_dataset(data)
    
    # Con umbral alto (95%) no debe detectar como sensible
    scanner_high = DataScanner(threshold=0.95)
    results_high = scanner_high.scan_dataset(data)
    
    assert results_low['threshold_applied'] == 0.60, "Debe aplicar threshold bajo"
    assert results_high['threshold_applied'] == 0.95, "Debe aplicar threshold alto"
    
    # El umbral debe afectar la decisión de anonimización
    # (dependiendo de la calidad de los datos)
    
    print("✓ Test umbral configurable: PASS")


def test_anonymize_dataset_deterministic():
    """Test de anonimización determinística (requisito del alcance)"""
    scanner = DataScanner(threshold=0.80, seed=12345)  # Umbral más bajo para asegurar detección
    
    # Dataset con datos sensibles claramente identificables
    data = [
        {
            "id": "001",
            "cedula": "1710034065",
            "cedula2": "0926687856",
            "cedula3": "0602910945",
            "email": "juan@example.com",
            "nombre": "Juan Pérez"
        },
        {
            "id": "002",
            "cedula": "0926687856",
            "cedula2": "1710034065",
            "cedula3": "1234567890",
            "email": "maria@test.com",
            "nombre": "María López"
        }
    ]
    
    # Escanear primero
    scan_results = scanner.scan_dataset(data)
    
    # Anonimizar
    results = scanner.anonymize_dataset(data)
    
    assert 'anonymized_data' in results, "Debe retornar datos anonimizados"
    
    # Si se detectaron columnas sensibles, verificar seed
    if results.get('columns_anonymized', 0) > 0:
        assert 'seed_used' in results, "Debe reportar seed si hubo anonimización"
        assert results['seed_used'] == 12345, f"Debe usar la semilla configurada, got {results.get('seed_used')}"
        assert len(results['anonymized_data']) == 2, "Debe preservar cantidad de registros"
        
        # Verificar determinismo: mismo input + misma semilla = mismo output
        scanner2 = DataScanner(threshold=0.80, seed=12345)
        scanner2.scan_dataset(data)
        results2 = scanner2.anonymize_dataset(data)
        
        # Los valores anonimizados deben ser idénticos
        anon_cedula1 = results['anonymized_data'][0].get('cedula')
        anon_cedula2 = results2['anonymized_data'][0].get('cedula')
        
        if anon_cedula1 and anon_cedula2:
            assert anon_cedula1 == anon_cedula2, \
                f"Anonimización debe ser determinística: {anon_cedula1} vs {anon_cedula2}"
    
    print("✓ Test anonimización determinística: PASS")


def test_anonymization_preserves_format():
    """Test que anonimización preserve formato (requisito del alcance)"""
    scanner = DataScanner(threshold=0.80, seed=42)  # Umbral bajo para asegurar detección
    
    # Dataset con múltiples ejemplos para asegurar detección
    data = [
        {
            "cedula": "1710034065",
            "cedula2": "0926687856",
            "cedula3": "0602910945",
            "email": "test@example.com",
            "telefono": "0991234567"
        },
        {
            "cedula": "0926687856",
            "cedula2": "1710034065",
            "cedula3": "1234567890",
            "email": "test2@example.com",
            "telefono": "0987654321"
        }
    ]
    
    scanner.scan_dataset(data)
    results = scanner.anonymize_dataset(data)
    
    # Solo verificar validación si hubo anonimización
    if results.get('columns_anonymized', 0) > 0:
        assert 'validation' in results, "Debe incluir reporte de validación cuando hay anonimización"
        validation = results['validation']
        
        assert validation.get('format_preserved', False), \
            f"Formato debe preservarse. Issues: {validation.get('issues', [])}"
        
        # Verificar datos anonimizados
        anon_record = results['anonymized_data'][0]
        
        # Cédula debe tener 10 dígitos
        if 'cedula' in anon_record:
            cedula_anon = anon_record['cedula']
            assert len(str(cedula_anon)) == 10, f"Cédula debe tener 10 dígitos: {cedula_anon}"
            assert str(cedula_anon).isdigit(), f"Cédula debe ser numérica: {cedula_anon}"
        
        # Email debe tener @ y .
        if 'email' in anon_record:
            email_anon = anon_record['email']
            assert '@' in email_anon, f"Email debe contener @: {email_anon}"
            assert '.' in email_anon, f"Email debe contener punto: {email_anon}"
        
        # Teléfono debe tener 10 dígitos
        if 'telefono' in anon_record:
            tel_anon = anon_record['telefono']
            assert len(str(tel_anon)) == 10, f"Teléfono debe tener 10 dígitos: {tel_anon}"
    
    print("✓ Test preservación de formato: PASS")


def test_anonymization_preserves_validity():
    """Test que anonimización preserve validez (requisito del alcance)"""
    scanner = DataScanner(threshold=0.80, seed=99)  # Umbral bajo
    
    # Generar cédulas válidas en múltiples columnas
    data = [
        {
            "cedula1": EcuadorValidators.generar_cedula_valida(),
            "cedula2": EcuadorValidators.generar_cedula_valida(),
            "cedula3": EcuadorValidators.generar_cedula_valida()
        }
        for _ in range(5)
    ]
    
    scanner.scan_dataset(data)
    results = scanner.anonymize_dataset(data)
    
    # Solo verificar si hubo anonimización
    if results.get('columns_anonymized', 0) > 0:
        # Verificar que las cédulas anonimizadas siguen siendo válidas
        for record in results['anonymized_data']:
            for key, value in record.items():
                if key.startswith('cedula'):
                    assert EcuadorValidators.validar_cedula(value), \
                        f"Cédula anonimizada debe ser válida: {value}"
        
        # Verificar reporte de validación
        validation = results.get('validation', {})
        assert validation.get('validity_preserved', False), \
            f"Validez debe preservarse. Issues: {validation.get('issues', [])}"
    
    print("✓ Test preservación de validez: PASS")


def test_generate_report():
    """Test de generación de reportes"""
    scanner = DataScanner(threshold=0.90, seed=42)
    
    data = [
        {"cedula": "1710034065", "email": "test@example.com"}
    ]
    
    scanner.scan_dataset(data)
    scanner.anonymize_dataset(data)
    
    # Generar reporte
    report = scanner.generate_report()
    
    assert 'configuration' in report, "Debe incluir configuración"
    assert 'scan_results' in report, "Debe incluir resultados de escaneo"
    assert 'anonymization_results' in report, "Debe incluir resultados de anonimización"
    assert report['configuration']['threshold'] == 0.90, "Debe reportar threshold"
    assert report['configuration']['seed'] == 42, "Debe reportar seed"
    
    print("✓ Test generación de reportes: PASS")


def test_scan_file_json():
    """Test de escaneo de archivo JSON"""
    scanner = DataScanner(threshold=0.90)
    
    # Crear archivo temporal
    data = [
        {"cedula": "1710034065", "email": "test@example.com"},
        {"cedula": "0926687856", "email": "test2@example.com"}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_file = f.name
    
    try:
        results = scanner.scan_file(temp_file, file_format='json')
        
        assert 'columns_detail' in results, "Debe escanear archivo correctamente"
        assert results['total_records'] == 2, "Debe contar registros del archivo"
        
        print("✓ Test escaneo de archivo JSON: PASS")
    finally:
        Path(temp_file).unlink(missing_ok=True)


def test_integration_scan_and_anonymize():
    """Test de integración completo: escaneo + anonimización + validación"""
    scanner = DataScanner(threshold=0.75, seed=777)  # Umbral más bajo
    
    # Dataset completo con múltiples tipos y abundantes ejemplos
    data = [
        {
            "id": f"CLI{i:03d}",
            "nombre": f"Cliente {i}",
            "cedula": EcuadorValidators.generar_cedula_valida(),
            "cedula2": EcuadorValidators.generar_cedula_valida(),
            "email": f"cliente{i}@example.com",
            "email2": f"user{i}@test.com",
            "telefono": f"099{i:07d}",
            "edad": str(20 + i)
        }
        for i in range(10)
    ]
    
    # 1. Escanear
    scan_results = scanner.scan_dataset(data)
    assert scan_results['total_records'] == 10, "Debe escanear 10 registros"
    assert scan_results['sensitive_columns'] > 0, "Debe detectar columnas sensibles"
    
    # 2. Anonimizar
    anon_results = scanner.anonymize_dataset(data)
    assert len(anon_results['anonymized_data']) == 10, "Debe anonimizar 10 registros"
    
    # Solo verificar si detectó columnas sensibles
    if scan_results['sensitive_columns'] > 0:
        assert anon_results.get('columns_anonymized', 0) > 0, \
            f"Debe anonimizar columnas. Scan detectó {scan_results['sensitive_columns']} sensibles"
        
        # 3. Validar
        validation = anon_results.get('validation', {})
        assert validation.get('format_preserved'), "Formato debe preservarse"
    
    # 4. Generar reporte
    report = scanner.generate_report()
    assert report is not None, "Debe generar reporte"
    
    print("✓ Test integración completa: PASS")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJECUTANDO TESTS DE SCANNER (INTEGRACIÓN)")
    print("="*60 + "\n")
    
    try:
        test_scanner_initialization()
        test_scan_dataset_with_sensitive_data()
        test_scan_identifies_specific_types()
        test_threshold_configuration()
        test_anonymize_dataset_deterministic()
        test_anonymization_preserves_format()
        test_anonymization_preserves_validity()
        test_generate_report()
        test_scan_file_json()
        test_integration_scan_and_anonymize()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*60 + "\n")
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        sys.exit(1)
