"""
Tests para el detector de datos sensibles
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anonymization.detector import SensitiveDataDetector


def test_detector_cedula():
    """Test de detección de cédulas"""
    detector = SensitiveDataDetector(threshold=0.9)
    
    # Columna con cédulas válidas
    cedulas = [
        "1710034065",
        "0926687856",
        "1234567890",  # Puede ser inválida
    ]
    
    result = detector.scan_column(cedulas, "cedula")
    assert result["type"] == "cedula", "Debe detectar tipo cedula"
    print("✓ Test detector de cédulas: PASS")


def test_detector_email():
    """Test de detección de emails"""
    detector = SensitiveDataDetector(threshold=0.9)
    
    emails = [
        "juan@example.com",
        "maria.perez@gmail.com",
        "contacto@empresa.ec",
    ]
    
    result = detector.scan_column(emails, "email")
    assert result["type"] == "email", "Debe detectar tipo email"
    assert result["probability"] > 0.9, "Probabilidad debe ser alta"
    print("✓ Test detector de emails: PASS")


def test_detector_telefono():
    """Test de detección de teléfonos"""
    detector = SensitiveDataDetector(threshold=0.9)
    
    telefonos = [
        "0991234567",
        "0987654321",
        "0961234567",
    ]
    
    result = detector.scan_column(telefonos, "telefono")
    assert result["type"] == "telefono", "Debe detectar tipo telefono"
    print("✓ Test detector de teléfonos: PASS")


def test_detector_threshold():
    """Test de threshold de detección"""
    # Detector con threshold alto
    detector_high = SensitiveDataDetector(threshold=0.95)
    
    # Mezcla de datos (50% válidos)
    mixed_data = [
        "juan@example.com",
        "no-es-email",
        "maria@test.com",
        "texto random",
    ]
    
    result = detector_high.scan_column(mixed_data, "test")
    # Con threshold alto, puede que no requiera anonimización si no supera el umbral
    assert "probability" in result, "Debe calcular probabilidad"
    print("✓ Test detector con threshold: PASS")


def test_scan_dataset():
    """Test de escaneo de dataset completo"""
    detector = SensitiveDataDetector(threshold=0.85)
    
    dataset = [
        {
            "nombre": "Juan Pérez",
            "cedula": "1710034065",
            "email": "juan@example.com",
            "edad": "30",
        },
        {
            "nombre": "María López",
            "cedula": "0926687856",
            "email": "maria@test.com",
            "edad": "25",
        },
    ]
    
    results = detector.scan_dataset(dataset)
    
    assert "cedula" in results, "Debe escanear columna cedula"
    assert "email" in results, "Debe escanear columna email"
    assert results["cedula"]["requires_anonymization"], "Cédula debe requerir anonimización"
    assert results["email"]["requires_anonymization"], "Email debe requerir anonimización"
    print("✓ Test scan_dataset: PASS")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJECUTANDO TESTS DE DETECTOR")
    print("="*60 + "\n")
    
    try:
        test_detector_cedula()
        test_detector_email()
        test_detector_telefono()
        test_detector_threshold()
        test_scan_dataset()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*60 + "\n")
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        sys.exit(1)
