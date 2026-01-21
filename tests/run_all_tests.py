"""
Script para ejecutar todos los tests del proyecto
"""
import sys
import subprocess
from pathlib import Path

# Directorio de tests
TEST_DIR = Path(__file__).parent

# Lista de archivos de test
TEST_FILES = [
    "test_validators_ec.py",
    "test_detector.py",
    "test_anonymizer.py",
    "test_cliente_generator.py",
]


def run_test(test_file):
    """Ejecuta un archivo de test"""
    print(f"\n{'='*70}")
    print(f"Ejecutando: {test_file}")
    print('='*70)
    
    test_path = TEST_DIR / test_file
    result = subprocess.run(
        [sys.executable, str(test_path)],
        capture_output=False,
        text=True
    )
    
    return result.returncode == 0


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*70)
    print(" "*20 + "SUITE COMPLETA DE TESTS")
    print("="*70)
    
    passed = 0
    failed = 0
    failed_tests = []
    
    for test_file in TEST_FILES:
        try:
            if run_test(test_file):
                passed += 1
            else:
                failed += 1
                failed_tests.append(test_file)
        except Exception as e:
            print(f"❌ Error ejecutando {test_file}: {e}")
            failed += 1
            failed_tests.append(test_file)
    
    # Resumen final
    print("\n" + "="*70)
    print(" "*25 + "RESUMEN FINAL")
    print("="*70)
    print(f"\n✅ Tests exitosos: {passed}/{len(TEST_FILES)}")
    
    if failed > 0:
        print(f"❌ Tests fallidos: {failed}/{len(TEST_FILES)}")
        print("\nTests que fallaron:")
        for test in failed_tests:
            print(f"  - {test}")
        sys.exit(1)
    else:
        print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
