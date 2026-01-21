"""
Demo del DataScanner - Integración de detección y anonimización.

Este demo muestra las capacidades completas del scanner:
1. Escaneo probabilístico de datasets
2. Identificación de tipos sensibles (Cédula, RUC, Email, Teléfono)
3. Umbral configurable (90% por defecto)
4. Anonimización determinística
5. Preservación de formato y validez
6. Generación de reportes
"""
import sys
from pathlib import Path
import json

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anonymization.scanner import DataScanner
from anonymization.validators_ec import EcuadorValidators


def demo_basic_scan():
    """Demo 1: Escaneo básico de dataset con datos sensibles"""
    print("\n" + "="*70)
    print(" "*15 + "DEMO 1: ESCANEO BÁSICO DE DATASET")
    print("="*70)
    
    # Crear scanner con threshold por defecto (90%)
    scanner = DataScanner(threshold=0.90, seed=12345)
    
    # Dataset con datos sensibles
    data = [
        {
            "id": "001",
            "nombre": "Juan Pérez",
            "cedula": "1710034065",
            "email": "juan.perez@example.com",
            "telefono": "0991234567",
            "ciudad": "Quito"
        },
        {
            "id": "002",
            "nombre": "María López",
            "cedula": "0926687856",
            "email": "maria.lopez@test.com",
            "telefono": "0987654321",
            "ciudad": "Guayaquil"
        },
        {
            "id": "003",
            "nombre": "Carlos Ruiz",
            "cedula": "0602910945",
            "email": "carlos.ruiz@demo.com",
            "telefono": "0981234567",
            "ciudad": "Cuenca"
        }
    ]
    
    print("\n📊 Dataset original (3 registros):")
    print(json.dumps(data[0], indent=2, ensure_ascii=False))
    
    # Escanear dataset
    print("\n🔍 Escaneando dataset...")
    scan_results = scanner.scan_dataset(data)
    
    print(f"\n📈 Resultados del escaneo:")
    print(f"   Total de registros: {scan_results['total_records']}")
    print(f"   Columnas escaneadas: {scan_results['columns_scanned']}")
    print(f"   Columnas sensibles detectadas: {scan_results['sensitive_columns']}")
    print(f"   Umbral aplicado: {scan_results['threshold_applied']*100}%")
    
    print(f"\n📋 Detalle por columna:")
    for col, info in scan_results['columns_detail'].items():
        tipo = info.get('type') or 'N/A'
        prob = info.get('probability', 0) * 100
        req = "SÍ" if info.get('requires_anonymization') else "NO"
        print(f"   - {col:15} Tipo: {tipo:15} Probabilidad: {prob:5.1f}%  Anonimizar: {req}")


def demo_threshold_comparison():
    """Demo 2: Comparación de diferentes umbrales"""
    print("\n" + "="*70)
    print(" "*15 + "DEMO 2: COMPARACIÓN DE UMBRALES")
    print("="*70)
    
    # Dataset con calidad variable
    data = [
        {"email": "valid@example.com"},
        {"email": "another@test.com"},
        {"email": "not-an-email"},  # 66% de emails válidos
    ]
    
    thresholds = [0.50, 0.70, 0.90]
    
    for threshold in thresholds:
        scanner = DataScanner(threshold=threshold)
        results = scanner.scan_dataset(data)
        
        email_info = results['columns_detail'].get('email', {})
        prob = email_info.get('probability', 0) * 100
        req = "SÍ" if email_info.get('requires_anonymization') else "NO"
        
        print(f"\nUmbral {threshold*100}%: Probabilidad={prob:.1f}% → Anonimizar: {req}")


def demo_anonymization():
    """Demo 3: Anonimización determinística preservando formato"""
    print("\n" + "="*70)
    print(" "*10 + "DEMO 3: ANONIMIZACIÓN DETERMINÍSTICA")
    print("="*70)
    
    scanner = DataScanner(threshold=0.80, seed=42)
    
    # Dataset con tipos variados
    data = [
        {
            "nombre": "Juan Pérez",
            "cedula": "1710034065",
            "ruc_natural": EcuadorValidators.generar_ruc_natural(),
            "ruc_empresa": EcuadorValidators.generar_ruc_empresa(),
            "email": "juan@example.com",
            "telefono": "0991234567",
            "edad": 30
        }
    ]
    
    print("\n📄 Registro original:")
    print(json.dumps(data[0], indent=2, ensure_ascii=False))
    
    # Escanear y anonimizar
    print("\n🔍 Escaneando y anonimizando...")
    scanner.scan_dataset(data)
    results = scanner.anonymize_dataset(data)
    
    print(f"\n📊 Resultado de la anonimización:")
    print(f"   Columnas anonimizadas: {results.get('columns_anonymized', 0)}")
    
    if results.get('anonymized_data'):
        print(f"\n📄 Registro anonimizado:")
        print(json.dumps(results['anonymized_data'][0], indent=2, ensure_ascii=False))
        
        # Verificar preservación de formato
        validation = results.get('validation', {})
        print(f"\n✅ Validación:")
        print(f"   Formato preservado: {'✓' if validation.get('format_preserved') else '✗'}")
        print(f"   Validez preservada: {'✓' if validation.get('validity_preserved') else '✗'}")
        
        if validation.get('issues'):
            print(f"\n⚠️  Problemas detectados:")
            for issue in validation['issues'][:3]:
                print(f"   - {issue}")


def demo_determinism():
    """Demo 4: Verificación de determinismo"""
    print("\n" + "="*70)
    print(" "*15 + "DEMO 4: VERIFICACIÓN DE DETERMINISMO")
    print("="*70)
    
    data = [{"cedula": "1710034065", "email": "test@example.com"}]
    
    # Primera ejecución
    scanner1 = DataScanner(threshold=0.80, seed=999)
    scanner1.scan_dataset(data)
    result1 = scanner1.anonymize_dataset(data)
    
    # Segunda ejecución con misma semilla
    scanner2 = DataScanner(threshold=0.80, seed=999)
    scanner2.scan_dataset(data)
    result2 = scanner2.anonymize_dataset(data)
    
    if result1.get('anonymized_data') and result2.get('anonymized_data'):
        anon1 = result1['anonymized_data'][0]
        anon2 = result2['anonymized_data'][0]
        
        print("\n🔒 Misma semilla (999):")
        print(f"   Ejecución 1: cedula={anon1.get('cedula')}, email={anon1.get('email')}")
        print(f"   Ejecución 2: cedula={anon2.get('cedula')}, email={anon2.get('email')}")
        print(f"   ✓ Idénticos: {anon1 == anon2}")
    
    # Tercera ejecución con diferente semilla
    scanner3 = DataScanner(threshold=0.80, seed=111)
    scanner3.scan_dataset(data)
    result3 = scanner3.anonymize_dataset(data)
    
    if result3.get('anonymized_data'):
        anon3 = result3['anonymized_data'][0]
        
        print(f"\n🔑 Diferente semilla (111):")
        print(f"   Ejecución 3: cedula={anon3.get('cedula')}, email={anon3.get('email')}")
        print(f"   ✓ Diferentes: {anon1 != anon3}")


def demo_report_generation():
    """Demo 5: Generación de reportes completos"""
    print("\n" + "="*70)
    print(" "*15 + "DEMO 5: GENERACIÓN DE REPORTES")
    print("="*70)
    
    scanner = DataScanner(threshold=0.85, seed=12345)
    
    data = [
        {
            "id": f"CLI{i:03d}",
            "cedula": EcuadorValidators.generar_cedula_valida(),
            "email": f"cliente{i}@example.com",
            "telefono": f"099{i:07d}"
        }
        for i in range(5)
    ]
    
    # Escanear y anonimizar
    scanner.scan_dataset(data)
    scanner.anonymize_dataset(data)
    
    # Generar reporte
    print("\n📋 Generando reporte completo...")
    report = scanner.generate_report()
    
    print(f"\n📊 Resumen del reporte:")
    print(f"   Timestamp: {report['scan_timestamp'][:19]}")
    print(f"   Threshold: {report['configuration']['threshold']*100}%")
    print(f"   Seed: {report['configuration']['seed']}")
    
    if report.get('scan_results'):
        scan = report['scan_results']
        print(f"\n🔍 Escaneo:")
        print(f"   Registros: {scan.get('total_records', 0)}")
        print(f"   Columnas sensibles: {scan.get('sensitive_columns', 0)}")
    
    if report.get('anonymization_results'):
        anon = report['anonymization_results']
        print(f"\n🔒 Anonimización:")
        print(f"   Columnas procesadas: {anon.get('columns_anonymized', 0)}")
        
        if anon.get('validation'):
            val = anon['validation']
            print(f"\n✅ Validación:")
            print(f"   Formato: {'✓' if val.get('format_preserved') else '✗'}")
            print(f"   Validez: {'✓' if val.get('validity_preserved') else '✗'}")


def demo_file_processing():
    """Demo 6: Procesamiento de archivos JSON"""
    print("\n" + "="*70)
    print(" "*15 + "DEMO 6: PROCESAMIENTO DE ARCHIVOS")
    print("="*70)
    
    # Crear archivo temporal
    test_data = [
        {
            "id": "001",
            "nombre": "Test User",
            "cedula": "1710034065",
            "email": "test@example.com"
        }
    ]
    
    temp_dir = Path(__file__).parent.parent / "data" / "output"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    input_file = temp_dir / "scanner_demo_input.json"
    output_file = temp_dir / "scanner_demo_output.json"
    
    # Guardar archivo de entrada
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Archivo de entrada: {input_file.name}")
    print(f"   Registros: {len(test_data)}")
    
    # Procesar archivo
    scanner = DataScanner(threshold=0.80, seed=555)
    results = scanner.anonymize_file(input_file, output_file, file_format='json')
    
    print(f"\n✅ Procesamiento completo:")
    print(f"   Archivo de salida: {output_file.name}")
    
    if 'message' in results:
        print(f"   {results['message']}")
    
    if results.get('anonymization_summary'):
        summary = results['anonymization_summary']
        print(f"   Columnas anonimizadas: {summary.get('columns_anonymized', 0)}")


def main():
    """Ejecuta todos los demos"""
    print("\n" + "="*70)
    print(" "*15 + "DEMO DEL DATASCANNER")
    print(" "*10 + "Integración Detector + Anonimizador")
    print("="*70)
    
    demo_basic_scan()
    demo_threshold_comparison()
    demo_anonymization()
    demo_determinism()
    demo_report_generation()
    demo_file_processing()
    
    print("\n" + "="*70)
    print(" "*20 + "FIN DE LOS DEMOS")
    print("="*70)
    print("\n✅ Requisitos del alcance demostrados:")
    print("   ✓ Identificación por muestreo con cálculo de probabilidad")
    print("   ✓ Tipos soportados: Cédula, RUC, Email, Teléfono")
    print("   ✓ Umbral configurable (90% por defecto)")
    print("   ✓ Anonimización determinística")
    print("   ✓ Preservación de formato")
    print("   ✓ Preservación de validez")
    print("   ✓ Generación de reportes")
    print("   ✓ Procesamiento de archivos")
    print()


if __name__ == "__main__":
    main()
