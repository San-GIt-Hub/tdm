"""
Script ejemplo del Desafío de Datos Sintéticos.
Genera clientes, inyecta fallas y valida el dataset.
"""
import json
import csv
from datetime import datetime
from cliente_generator import ClienteGenerator
from fault_injector import FaultInjector
from cliente_validator import ClienteValidator


def main():
    """Ejecuta el flujo completo del desafío de datos sintéticos."""
    
    # Configuración
    SEED = 42
    NUM_CLIENTES = 100  # Parametrizable: 100-500
    FAULT_RATE = 0.0005  # 0.05% de errores
    
    print("=" * 80)
    print("DESAFÍO DE DATOS SINTÉTICOS - TDM")
    print("=" * 80)
    print(f"\nConfiguración:")
    print(f"  - Semilla: {SEED}")
    print(f"  - Número de clientes: {NUM_CLIENTES}")
    print(f"  - Tasa de error: {FAULT_RATE} ({FAULT_RATE * 100}%)")
    print(f"  - Errores esperados: ~{int(NUM_CLIENTES * FAULT_RATE)}")
    
    # Paso 1: Generar datos sintéticos
    print("\n" + "-" * 80)
    print("PASO 1: Generación de datos sintéticos")
    print("-" * 80)
    generator = ClienteGenerator(locale='es_ES', seed=SEED)
    clientes_limpios = generator.generate_clientes(count=NUM_CLIENTES)
    print(f"✓ Generados {len(clientes_limpios)} clientes sintéticos")
    print(f"\nEjemplo de cliente generado:")
    print(json.dumps(clientes_limpios[0], indent=2, ensure_ascii=False))
    
    # Paso 2: Inyectar fallas
    print("\n" + "-" * 80)
    print("PASO 2: Inyección de fallas")
    print("-" * 80)
    injector = FaultInjector(fault_rate=FAULT_RATE, seed=SEED)
    clientes_con_errores, error_log = injector.inject_faults(clientes_limpios)
    
    print(f"✓ Errores inyectados: {error_log['total_errors_injected']}")
    print(f"\nErrores por tipo:")
    for error_type, errors in error_log['errors_by_type'].items():
        print(f"  - {error_type}: {len(errors)}")
    
    # Paso 3: Validar dataset
    print("\n" + "-" * 80)
    print("PASO 3: Validación determinística")
    print("-" * 80)
    validator = ClienteValidator()
    reporte = validator.validate_dataset(clientes_con_errores)
    
    print(f"\n📊 REPORTE DE VALIDACIÓN:")
    print(f"  Total de registros: {reporte['total_registros']}")
    print(f"  Errores totales encontrados: {reporte['errores_totales']}")
    print(f"  Porcentaje de cumplimiento: {reporte['porcentaje_cumplimiento']}%")
    
    print(f"\n  Errores por tipo:")
    for tipo, cantidad in reporte['errores_por_tipo'].items():
        print(f"    - {tipo}: {cantidad}")
    
    print(f"\n  Reglas evaluadas:")
    for regla in reporte['reglas_evaluadas']:
        print(f"    • {regla}")
    
    # Mostrar muestras de errores
    print(f"\n  📋 Muestras de errores encontrados:")
    for tipo, errores in reporte['muestras_de_errores'].items():
        if errores:
            print(f"\n    {tipo.upper()}:")
            for error in errores[:3]:  # Mostrar solo los 3 primeros
                print(f"      - [{error.get('customer_id')}] {error.get('description')}")
    
    # Paso 4: Guardar resultados
    print("\n" + "-" * 80)
    print("PASO 4: Guardando resultados")
    print("-" * 80)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    base_filename = f"clientes_{timestamp}_seed{SEED}"
    
    # Guardar dataset en JSON
    json_filename = f"../data/output/{base_filename}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(clientes_con_errores, f, indent=2, ensure_ascii=False)
    print(f"✓ Dataset guardado: {json_filename}")
    
    # Guardar dataset en CSV
    csv_filename = f"../data/output/{base_filename}.csv"
    if clientes_con_errores:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=clientes_con_errores[0].keys())
            writer.writeheader()
            writer.writerows(clientes_con_errores)
        print(f"✓ Dataset guardado: {csv_filename}")
    
    # Guardar reporte de validación
    reporte_filename = f"../reports/validation_report_{timestamp}_seed{SEED}.json"
    with open(reporte_filename, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    print(f"✓ Reporte de validación guardado: {reporte_filename}")
    
    # Guardar log de errores inyectados
    log_filename = f"../reports/injection_log_{timestamp}_seed{SEED}.json"
    with open(log_filename, 'w', encoding='utf-8') as f:
        json.dump(error_log, f, indent=2, ensure_ascii=False)
    print(f"✓ Log de inyección guardado: {log_filename}")
    
    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    
    # Resumen final
    print(f"\n📈 RESUMEN:")
    print(f"  • Clientes generados: {NUM_CLIENTES}")
    print(f"  • Errores inyectados: {error_log['total_errors_injected']}")
    print(f"  • Errores detectados: {reporte['errores_totales']}")
    print(f"  • Precisión de detección: {(reporte['errores_totales'] / max(1, error_log['total_errors_injected']) * 100):.1f}%")
    print(f"  • Cumplimiento de contrato: {reporte['porcentaje_cumplimiento']}%")


if __name__ == "__main__":
    main()
