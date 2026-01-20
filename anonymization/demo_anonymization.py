"""
Script ejemplo del Desafío de Anonimización.
Escanea, detecta y anonimiza datos sensibles preservando formato e integridad referencial.
"""
import json
import csv
from datetime import datetime
import sys
import os

# Agregar directorios al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anonymization.detector import SensitiveDataDetector
from anonymization.anonymizer import DataAnonymizer
from anonymization.rules import AnonymizationRule, RuleEngine


def generar_datos_ejemplo():
    """Genera datos de ejemplo para demostrar la anonimización."""
    return [
        {
            'cliente_id': 1,
            'nombre': 'María García',
            'cedula': '1713456789',
            'email': 'maria.garcia@banco.com',
            'telefono': '0987654321',
            'direccion': 'Av. Amazonas N45-32',
            'ruc_empresa': '1790123456001'
        },
        {
            'cliente_id': 2,
            'nombre': 'Juan Pérez',
            'cedula': '0912345678',
            'email': 'juan.perez@banco.com',
            'telefono': '0998765432',
            'direccion': 'Calle 10 de Agosto y Patria',
            'ruc_empresa': '1790987654001'
        },
        {
            'cliente_id': 3,
            'nombre': 'Ana Rodríguez',
            'cedula': '1710234567',
            'email': 'ana.rodriguez@banco.com',
            'telefono': '0991234567',
            'direccion': 'Av. 6 de Diciembre N34-123',
            'ruc_empresa': '1790555444001'
        },
        {
            'cliente_id': 4,
            'nombre': 'Carlos López',
            'cedula': '0923456789',
            'email': 'carlos.lopez@banco.com',
            'telefono': '0987777888',
            'direccion': 'Av. Naciones Unidas E4-125',
            'ruc_empresa': '1790111222001'
        },
        {
            'cliente_id': 5,
            'nombre': 'Lucía Fernández',
            'cedula': '1723456789',
            'email': 'lucia.fernandez@banco.com',
            'telefono': '0993334455',
            'direccion': 'Calle Colón y Reina Victoria',
            'ruc_empresa': '1790666777001'
        }
    ]


def main():
    """Ejecuta el flujo completo del desafío de anonimización."""
    
    # Configuración
    SEED = 12345
    THRESHOLD = 0.90  # Umbral de probabilidad para anonimización (90%)
    
    print("=" * 80)
    print("DESAFÍO DE ANONIMIZACIÓN - TDM")
    print("=" * 80)
    print(f"\nConfiguración:")
    print(f"  - Semilla maestra: {SEED}")
    print(f"  - Umbral de detección: {THRESHOLD} ({THRESHOLD * 100}%)")
    
    # Paso 1: Cargar datos de ejemplo
    print("\n" + "-" * 80)
    print("PASO 1: Datos originales")
    print("-" * 80)
    datos_originales = generar_datos_ejemplo()
    print(f"✓ Cargados {len(datos_originales)} registros")
    print(f"\nEjemplo de registro original:")
    print(json.dumps(datos_originales[0], indent=2, ensure_ascii=False))
    
    # Paso 2: Escanear y detectar datos sensibles
    print("\n" + "-" * 80)
    print("PASO 2: Escaneo y detección de datos sensibles")
    print("-" * 80)
    detector = SensitiveDataDetector(threshold=THRESHOLD)
    scan_results = detector.scan_dataset(datos_originales)
    
    print(f"\n📊 Resultados del escaneo por columna:")
    for columna, resultado in scan_results.items():
        print(f"\n  Columna: {columna}")
        print(f"    - Tipo detectado: {resultado['type']}")
        print(f"    - Probabilidad: {resultado['probability']:.2%}")
        print(f"    - Requiere anonimización: {'SÍ' if resultado['requires_anonymization'] else 'NO'}")
        if resultado['requires_anonymization']:
            print(f"    - Muestra analizada: {resultado['sample_size']} de {resultado['total_records']}")
    
    # Paso 3: Crear reglas de anonimización
    print("\n" + "-" * 80)
    print("PASO 3: Creación de reglas de anonimización")
    print("-" * 80)
    engine = RuleEngine()
    
    for columna, resultado in scan_results.items():
        if resultado['requires_anonymization']:
            tipo = resultado['type']
            
            # Determinar método de anonimización según el tipo
            if tipo in ['cedula', 'ruc_natural', 'ruc_empresa']:
                metodo = 'pseudonymize'
                print(f"  ✓ {columna}: Pseudonimización (tipo: {tipo})")
            elif tipo == 'email':
                metodo = 'pseudonymize'
                print(f"  ✓ {columna}: Pseudonimización (tipo: {tipo})")
            elif tipo == 'telefono':
                metodo = 'pseudonymize'
                print(f"  ✓ {columna}: Pseudonimización (tipo: {tipo})")
            else:
                metodo = 'mask'
                print(f"  ✓ {columna}: Enmascaramiento (tipo: {tipo})")
            
            regla = AnonymizationRule(
                field_name=columna,
                data_type=tipo,
                method=metodo
            )
            engine.add_rule(regla)
    
    print(f"\n  Total de reglas creadas: {len(engine.rules)}")
    
    # Paso 4: Aplicar anonimización determinística
    print("\n" + "-" * 80)
    print("PASO 4: Anonimización determinística")
    print("-" * 80)
    anonymizer = DataAnonymizer(locale='es_ES', master_seed=SEED)
    datos_anonimizados = anonymizer.anonymize_dataset(datos_originales, engine)
    
    print(f"✓ {len(datos_anonimizados)} registros anonimizados")
    print(f"\nEjemplo de registro anonimizado:")
    print(json.dumps(datos_anonimizados[0], indent=2, ensure_ascii=False))
    
    # Paso 5: Verificar determinismo
    print("\n" + "-" * 80)
    print("PASO 5: Verificación de determinismo")
    print("-" * 80)
    
    # Anonimizar nuevamente con la misma semilla
    anonymizer2 = DataAnonymizer(locale='es_ES', master_seed=SEED)
    datos_anonimizados2 = anonymizer2.anonymize_dataset(datos_originales, engine)
    
    # Comparar resultados
    determinismo_ok = True
    for i, (reg1, reg2) in enumerate(zip(datos_anonimizados, datos_anonimizados2)):
        if reg1 != reg2:
            determinismo_ok = False
            print(f"❌ Registro {i} NO coincide")
            break
    
    if determinismo_ok:
        print(f"✓ DETERMINISMO VERIFICADO: Dos ejecuciones con la misma semilla producen resultados idénticos")
    
    # Paso 6: Comparar original vs anonimizado
    print("\n" + "-" * 80)
    print("PASO 6: Comparación Original vs Anonimizado")
    print("-" * 80)
    
    print(f"\n{'Campo':<20} {'Original':<30} {'Anonimizado':<30}")
    print("-" * 80)
    original = datos_originales[0]
    anonimizado = datos_anonimizados[0]
    
    for campo in original.keys():
        val_orig = str(original[campo])[:28]
        val_anon = str(anonimizado[campo])[:28]
        print(f"{campo:<20} {val_orig:<30} {val_anon:<30}")
    
    # Paso 7: Verificar preservación de formato
    print("\n" + "-" * 80)
    print("PASO 7: Verificación de preservación de formato")
    print("-" * 80)
    
    formatos_preservados = True
    for campo in ['cedula', 'telefono']:
        if campo in original and campo in anonimizado:
            len_orig = len(str(original[campo]))
            len_anon = len(str(anonimizado[campo]))
            if len_orig == len_anon:
                print(f"  ✓ {campo}: Longitud preservada ({len_orig} caracteres)")
            else:
                print(f"  ❌ {campo}: Longitud NO preservada (orig: {len_orig}, anon: {len_anon})")
                formatos_preservados = False
    
    if formatos_preservados:
        print(f"\n✓ FORMATOS PRESERVADOS correctamente")
    
    # Paso 8: Guardar resultados
    print("\n" + "-" * 80)
    print("PASO 8: Guardando resultados")
    print("-" * 80)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    base_filename = f"anonymization_{timestamp}_seed{SEED}"
    
    # Guardar datos originales
    original_json = f"../data/output/{base_filename}_original.json"
    with open(original_json, 'w', encoding='utf-8') as f:
        json.dump(datos_originales, f, indent=2, ensure_ascii=False)
    print(f"✓ Datos originales: {original_json}")
    
    # Guardar datos anonimizados
    anonymized_json = f"../data/output/{base_filename}_anonymized.json"
    with open(anonymized_json, 'w', encoding='utf-8') as f:
        json.dump(datos_anonimizados, f, indent=2, ensure_ascii=False)
    print(f"✓ Datos anonimizados: {anonymized_json}")
    
    # Guardar reporte de escaneo
    scan_report = {
        'timestamp': timestamp,
        'seed': SEED,
        'threshold': THRESHOLD,
        'total_records': len(datos_originales),
        'columns_scanned': len(scan_results),
        'columns_requiring_anonymization': sum(1 for r in scan_results.values() if r['requires_anonymization']),
        'scan_results': scan_results,
        'rules_applied': [
            {
                'field': rule.field_name,
                'data_type': rule.data_type,
                'method': rule.method
            }
            for rule in engine.rules
        ]
    }
    
    report_json = f"../reports/anonymization_report_{timestamp}_seed{SEED}.json"
    with open(report_json, 'w', encoding='utf-8') as f:
        json.dump(scan_report, f, indent=2, ensure_ascii=False)
    print(f"✓ Reporte de anonimización: {report_json}")
    
    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    
    # Resumen final
    print(f"\n📈 RESUMEN:")
    print(f"  • Registros procesados: {len(datos_originales)}")
    print(f"  • Columnas escaneadas: {len(scan_results)}")
    print(f"  • Columnas anonimizadas: {sum(1 for r in scan_results.values() if r['requires_anonymization'])}")
    print(f"  • Determinismo: {'✓ Verificado' if determinismo_ok else '❌ Fallido'}")
    print(f"  • Formato preservado: {'✓ Sí' if formatos_preservados else '❌ No'}")


if __name__ == "__main__":
    main()
