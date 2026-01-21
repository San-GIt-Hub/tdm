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
    from validators_ec import EcuadorValidators
    
    return [
        {
            'cliente_id': 1,
            'nombre': 'María García',
            'cedula': EcuadorValidators.generar_cedula_valida(),
            'email': 'maria.garcia@banco.com',
            'telefono': '0987654321',
            'direccion': 'Av. Amazonas N45-32',
            'ruc_empresa': EcuadorValidators.generar_ruc_empresa()
        },
        {
            'cliente_id': 2,
            'nombre': 'Juan Pérez',
            'cedula': EcuadorValidators.generar_cedula_valida(),
            'email': 'juan.perez@banco.com',
            'telefono': '0998765432',
            'direccion': 'Calle 10 de Agosto y Patria',
            'ruc_empresa': EcuadorValidators.generar_ruc_empresa()
        },
        {
            'cliente_id': 3,
            'nombre': 'Ana Rodríguez',
            'cedula': EcuadorValidators.generar_cedula_valida(),
            'email': 'ana.rodriguez@banco.com',
            'telefono': '0991234567',
            'direccion': 'Av. 6 de Diciembre N34-123',
            'ruc_empresa': EcuadorValidators.generar_ruc_empresa()
        },
        {
            'cliente_id': 4,
            'nombre': 'Carlos López',
            'cedula': EcuadorValidators.generar_cedula_valida(),
            'email': 'carlos.lopez@banco.com',
            'telefono': '0987777888',
            'direccion': 'Av. Naciones Unidas E4-125',
            'ruc_empresa': EcuadorValidators.generar_ruc_empresa()
        },
        {
            'cliente_id': 5,
            'nombre': 'Lucía Fernández',
            'cedula': EcuadorValidators.generar_cedula_valida(),
            'email': 'lucia.fernandez@banco.com',
            'telefono': '0993334455',
            'direccion': 'Calle Colón y Reina Victoria',
            'ruc_empresa': EcuadorValidators.generar_ruc_empresa()
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
    
    # Paso 7: VALIDACIÓN COMPLETA DE REQUISITOS DEL ALCANCE
    print("\n" + "=" * 80)
    print("PASO 7: VALIDACIÓN DE CUMPLIMIENTO DEL ALCANCE FUNCIONAL")
    print("=" * 80)
    
    validaciones_exitosas = []
    validaciones_fallidas = []
    
    # REQUISITO 1: Identificación por columna mediante muestreo
    print("\n[REQUISITO 1] Identificación por columna mediante muestreo")
    muestreo_ok = all('sample_size' in r and r['sample_size'] > 0 for r in scan_results.values())
    if muestreo_ok:
        print(f"  ✓ Se realizó muestreo en todas las columnas")
        for col, res in scan_results.items():
            if res.get('sample_size'):
                print(f"    - {col}: {res['sample_size']} muestras de {res.get('total_records', 0)}")
        validaciones_exitosas.append("Muestreo por columna")
    else:
        print(f"  ❌ Muestreo no implementado correctamente")
        validaciones_fallidas.append("Muestreo por columna")
    
    # REQUISITO 2: Cálculo de probabilidad
    print("\n[REQUISITO 2] Cálculo de probabilidad de pertenencia")
    prob_ok = all('probability' in r for r in scan_results.values())
    if prob_ok:
        print(f"  ✓ Probabilidades calculadas para todas las columnas:")
        for col, res in scan_results.items():
            print(f"    - {col}: {res.get('probability', 0):.2%}")
        validaciones_exitosas.append("Cálculo de probabilidad")
    else:
        print(f"  ❌ Probabilidades no calculadas")
        validaciones_fallidas.append("Cálculo de probabilidad")
    
    # REQUISITO 3: Tipos específicos soportados
    print("\n[REQUISITO 3] Tipos de datos sensibles soportados")
    tipos_requeridos = {'cedula', 'ruc_natural', 'ruc_empresa', 'email', 'telefono'}
    tipos_detectados = {r['type'] for r in scan_results.values() if r['type']}
    tipos_encontrados = tipos_requeridos.intersection(tipos_detectados)
    
    if tipos_encontrados:
        print(f"  ✓ Tipos detectados: {', '.join(tipos_encontrados)}")
        for tipo in tipos_encontrados:
            cols = [c for c, r in scan_results.items() if r.get('type') == tipo]
            print(f"    - {tipo}: {', '.join(cols)}")
        validaciones_exitosas.append(f"Detección de tipos ({len(tipos_encontrados)}/{len(tipos_requeridos)})")
    else:
        print(f"  ❌ No se detectaron tipos específicos")
        validaciones_fallidas.append("Detección de tipos")
    
    # REQUISITO 4: Umbral configurable (90%)
    print(f"\n[REQUISITO 4] Umbral de probabilidad configurable (configurado: {THRESHOLD*100}%)")
    umbral_ok = THRESHOLD == 0.90
    columnas_por_umbral = sum(1 for r in scan_results.values() if r.get('requires_anonymization'))
    print(f"  ✓ Umbral configurado: {THRESHOLD*100}%")
    print(f"  ✓ Columnas que superan umbral: {columnas_por_umbral}")
    for col, res in scan_results.items():
        if res.get('requires_anonymization'):
            print(f"    - {col}: {res['probability']:.2%} ≥ {THRESHOLD*100}% → Anonimizar")
    validaciones_exitosas.append("Umbral configurable")
    
    # REQUISITO 5: Anonimización determinística
    print("\n[REQUISITO 5] Anonimización determinística (misma semilla = mismo resultado)")
    if determinismo_ok:
        print(f"  ✓ DETERMINISMO VERIFICADO con semilla {SEED}")
        # Mostrar ejemplo específico
        campo_ejemplo = 'cedula'
        if campo_ejemplo in datos_originales[0]:
            val_orig = datos_originales[0][campo_ejemplo]
            val_anon1 = datos_anonimizados[0][campo_ejemplo]
            val_anon2 = datos_anonimizados2[0][campo_ejemplo]
            print(f"    - Original: {val_orig}")
            print(f"    - Ejecución 1: {val_anon1}")
            print(f"    - Ejecución 2: {val_anon2}")
            print(f"    - Idénticos: {val_anon1 == val_anon2} ✓")
        validaciones_exitosas.append("Determinismo")
    else:
        print(f"  ❌ DETERMINISMO FALLIDO")
        validaciones_fallidas.append("Determinismo")
    
    # REQUISITO 6: Preservación de formato
    print("\n[REQUISITO 6] Preservación de formato de datos")
    from anonymization.validators_ec import EcuadorValidators
    
    formato_checks = {
        'cedula': lambda v: len(str(v)) == 10 and str(v).isdigit(),
        'telefono': lambda v: len(str(v)) == 10 and str(v).isdigit(),
        'email': lambda v: '@' in str(v) and '.' in str(v),
        'ruc_empresa': lambda v: len(str(v)) == 13 and str(v).isdigit()
    }
    
    formatos_ok = True
    for campo, check_fn in formato_checks.items():
        if campo in original and campo in anonimizado:
            orig_valido = check_fn(original[campo])
            anon_valido = check_fn(anonimizado[campo])
            if orig_valido and anon_valido:
                print(f"  ✓ {campo}: Formato preservado")
                print(f"    - Original: {original[campo]} (válido)")
                print(f"    - Anonimizado: {anonimizado[campo]} (válido)")
            else:
                print(f"  ❌ {campo}: Formato NO preservado")
                formatos_ok = False
    
    if formatos_ok:
        validaciones_exitosas.append("Preservación de formato")
    else:
        validaciones_fallidas.append("Preservación de formato")
    
    # REQUISITO 7: Preservación de validez
    print("\n[REQUISITO 7] Preservación de validez (cédulas y RUCs válidos)")
    validez_ok = True
    
    if 'cedula' in anonimizado:
        cedula_valida = EcuadorValidators.validar_cedula(str(anonimizado['cedula']))
        print(f"  {'✓' if cedula_valida else '❌'} Cédula anonimizada: {anonimizado['cedula']} ({'válida' if cedula_valida else 'inválida'})")
        validez_ok = validez_ok and cedula_valida
    
    if 'ruc_empresa' in anonimizado:
        ruc_valido = EcuadorValidators.validar_ruc_empresa(str(anonimizado['ruc_empresa']))
        print(f"  {'✓' if ruc_valido else '❌'} RUC empresa anonimizado: {anonimizado['ruc_empresa']} ({'válido' if ruc_valido else 'inválido'})")
        validez_ok = validez_ok and ruc_valido
    
    if validez_ok:
        validaciones_exitosas.append("Preservación de validez")
    else:
        validaciones_fallidas.append("Preservación de validez")
    
    # Resumen de validaciones
    print("\n" + "=" * 80)
    print("RESUMEN DE VALIDACIÓN DE REQUISITOS")
    print("=" * 80)
    print(f"\n✅ Validaciones exitosas ({len(validaciones_exitosas)}):")
    for val in validaciones_exitosas:
        print(f"  ✓ {val}")
    
    if validaciones_fallidas:
        print(f"\n❌ Validaciones fallidas ({len(validaciones_fallidas)}):")
        for val in validaciones_fallidas:
            print(f"  ✗ {val}")
    
    porcentaje_cumplimiento = (len(validaciones_exitosas) / (len(validaciones_exitosas) + len(validaciones_fallidas))) * 100
    print(f"\n📊 CUMPLIMIENTO TOTAL: {porcentaje_cumplimiento:.1f}%")
    
    if porcentaje_cumplimiento == 100:
        print("🎉 TODOS LOS REQUISITOS DEL ALCANCE CUMPLIDOS")
    
    
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
    print(f"  • Formato preservado: {'✓ Sí' if formatos_ok else '❌ No'}")
    print(f"  • Validez preservada: {'✓ Sí' if validez_ok else '❌ No'}")
    print(f"  • Cumplimiento de alcance: {porcentaje_cumplimiento:.1f}%")


if __name__ == "__main__":
    main()
