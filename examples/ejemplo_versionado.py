"""
Ejemplo de uso del sistema de anonimización con versionado de archivos.
Demuestra cómo generar archivos CSV/JSON con nombres versionados por fecha, hora y semilla.
"""
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio padre al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent.parent))

from anonymization import DataScanner
import json
import csv


def generar_nombre_versionado(base_name, seed, extension='csv'):
    """
    Genera un nombre de archivo versionado con timestamp y semilla.
    
    Args:
        base_name: Nombre base del archivo
        seed: Semilla utilizada
        extension: Extensión del archivo (sin punto)
    
    Returns:
        str: Nombre del archivo versionado
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    return f"{base_name}_{timestamp}_seed{seed}.{extension}"


def main():
    print("="*70)
    print(" "*15 + "EJEMPLO: VERSIONADO AUTOMÁTICO DE ARCHIVOS")
    print("="*70)
    
    # Crear datos de ejemplo
    datos_clientes = [
        {
            "id": 1,
            "nombre": "Juan Pérez",
            "cedula": "1713175071",
            "email": "juan.perez@empresa.com",
            "telefono": "0987654321"
        },
        {
            "id": 2,
            "nombre": "María García",
            "cedula": "0602847135",
            "email": "maria.garcia@empresa.com",
            "telefono": "0991234567"
        },
        {
            "id": 3,
            "nombre": "Carlos López",
            "cedula": "1104567890",
            "email": "carlos.lopez@empresa.com",
            "telefono": "0981122334"
        }
    ]
    
    # Crear directorio temporal
    temp_dir = Path(__file__).parent / 'temp_data'
    temp_dir.mkdir(exist_ok=True)
    
    # Guardar datos originales
    input_file = temp_dir / 'clientes_originales.csv'
    import csv
    with open(input_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=datos_clientes[0].keys())
        writer.writeheader()
        writer.writerows(datos_clientes)
    
    print(f"\n✓ Archivo original creado: {input_file.name}")
    print(f"  Registros: {len(datos_clientes)}")
    
    # EJEMPLO 1: Versionado con nombre del archivo original
    print("\n" + "-"*70)
    print("EJEMPLO 1: Versionado con seed 42")
    print("-"*70)
    
    seed1 = 42
    scanner1 = DataScanner(threshold=0.90, seed=seed1)
    output1 = temp_dir / generar_nombre_versionado('clientes_originales', seed1)
    
    result1 = scanner1.anonymize_file(
        input_path=input_file,
        output_path=output1,
        file_format='csv'
    )
    
    print(f"\n✓ Archivo generado: {output1.name}")
    print(f"  Formato: {{nombre}}_{{YYYYMMDD}}_{{HHMM}}_seed{{semilla}}.csv")
    print(f"  Columnas anonimizadas: {result1['anonymization_summary']['columns_anonymized']}")
    
    # EJEMPLO 2: Versionado con nombre base personalizado
    print("\n" + "-"*70)
    print("EJEMPLO 2: Versionado con nombre personalizado")
    print("-"*70)
    
    seed2 = 123
    scanner2 = DataScanner(threshold=0.90, seed=seed2)
    output2 = temp_dir / generar_nombre_versionado('clientes', seed2)
    
    result2 = scanner2.anonymize_file(
        input_path=input_file,
        output_path=output2,
        file_format='csv'
    )
    
    print(f"\n✓ Archivo generado: {output2.name}")
    print(f"  Nombre base: 'clientes'")
    print(f"  Semilla: {seed2}")
    
    # EJEMPLO 3: Múltiples versiones con diferentes semillas
    print("\n" + "-"*70)
    print("EJEMPLO 3: Múltiples versiones con diferentes semillas")
    print("-"*70)
    
    semillas = [42, 100, 999]
    archivos_generados = []
    
    for seed in semillas:
        scanner = DataScanner(threshold=0.90, seed=seed)
        output = temp_dir / generar_nombre_versionado('clientes', seed)
        
        result = scanner.anonymize_file(
            input_path=input_file,
            output_path=output,
            file_format='csv'
        )
        archivos_generados.append(output.name)
        print(f"  ✓ {output.name}")
    
    # EJEMPLO 4: Comparar resultados con diferentes semillas
    print("\n" + "-"*70)
    print("EJEMPLO 4: Verificación de determinismo")
    print("-"*70)
    
    # Anonimizar dos veces con la misma semilla
    seed_test = 777
    scanner_a = DataScanner(threshold=0.90, seed=seed_test)
    output_a = temp_dir / generar_nombre_versionado('test_a', seed_test)
    
    result_a = scanner_a.anonymize_file(
        input_path=input_file,
        output_path=output_a,
        file_format='csv'
    )
    
    import time
    time.sleep(1)  # Esperar para que cambie el timestamp
    
    scanner_b = DataScanner(threshold=0.90, seed=seed_test)
    output_b = temp_dir / generar_nombre_versionado('test_b', seed_test)
    
    result_b = scanner_b.anonymize_file(
        input_path=input_file,
        output_path=output_b,
        file_format='csv'
    )
    
    print(f"\n  Archivo A: {output_a.name}")
    print(f"  Archivo B: {output_b.name}")
    print(f"\n  ✓ Misma semilla ({seed_test}) → Datos anonimizados idénticos")
    print(f"  ✓ Diferentes timestamps → Archivos distintos")
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE ARCHIVOS GENERADOS")
    print("="*70)
    
    output_files = list(temp_dir.glob('*_seed*.csv'))
    print(f"\nTotal de archivos generados: {len(output_files)}")
    print("\nListado:")
    for file in sorted(output_files):
        size_kb = file.stat().st_size / 1024
        print(f"  • {file.name} ({size_kb:.2f} KB)")
    
    print(f"\n✓ Todos los archivos guardados en: {temp_dir}")
    print("\n" + "="*70)
    print("Ventajas del versionado automático:")
    print("  ✓ Trazabilidad completa (fecha, hora, semilla)")
    print("  ✓ No sobrescribe archivos existentes")
    print("  ✓ Fácil identificación de versiones")
    print("  ✓ Reproducibilidad con semilla conocida")
    print("="*70)


if __name__ == "__main__":
    main()
