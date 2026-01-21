"""
Tests para el anonimizador determinístico
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anonymization.anonymizer import DataAnonymizer
from anonymization.validators_ec import EcuadorValidators
import re

validar_cedula = EcuadorValidators.validar_cedula

def validar_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def test_pseudonymize_deterministic():
    """Test de pseudonimización determinística"""
    anonymizer = DataAnonymizer(master_seed=12345)
    
    # Mismo valor con mismo seed debe producir mismo resultado
    valor = "dato_sensible"
    result1 = anonymizer.pseudonymize(valor, "generico")
    result2 = anonymizer.pseudonymize(valor, "generico")
    
    assert result1 == result2, "Pseudonimización debe ser determinística"
    assert result1 != valor, "Valor debe estar anonimizado"
    print("✓ Test pseudonimización determinística: PASS")


def test_pseudonymize_cedula():
    """Test de pseudonimización de cédula preservando formato"""
    anonymizer = DataAnonymizer(master_seed=12345)
    
    cedula_original = "1710034065"
    cedula_anonimizada = anonymizer.pseudonymize(cedula_original, "cedula")
    
    assert len(cedula_anonimizada) == 10, "Cédula debe mantener 10 dígitos"
    assert cedula_anonimizada.isdigit(), "Cédula debe ser numérica"
    assert validar_cedula(cedula_anonimizada), "Cédula anonimizada debe ser válida"
    assert cedula_anonimizada != cedula_original, "Cédula debe estar anonimizada"
    print("✓ Test pseudonimización de cédula: PASS")


def test_pseudonymize_email():
    """Test de pseudonimización de email preservando formato"""
    anonymizer = DataAnonymizer(master_seed=12345)
    
    email_original = "juan.perez@example.com"
    email_anonimizado = anonymizer.pseudonymize(email_original, "email")
    
    assert "@" in email_anonimizado, "Email debe contener @"
    assert validar_email(email_anonimizado), "Email anonimizado debe ser válido"
    assert email_anonimizado != email_original, "Email debe estar anonimizado"
    print("✓ Test pseudonimización de email: PASS")


def test_pseudonymize_telefono():
    """Test de pseudonimización de teléfono preservando formato"""
    anonymizer = DataAnonymizer(master_seed=12345)
    
    telefono_original = "0991234567"
    telefono_anonimizado = anonymizer.pseudonymize(telefono_original, "telefono")
    
    assert len(telefono_anonimizado) == 10, "Teléfono debe tener 10 dígitos"
    assert telefono_anonimizado.startswith("09"), "Teléfono debe empezar con 09"
    assert telefono_anonimizado.isdigit(), "Teléfono debe ser numérico"
    assert telefono_anonimizado != telefono_original, "Teléfono debe estar anonimizado"
    print("✓ Test pseudonimización de teléfono: PASS")


def test_mask():
    """Test de enmascaramiento"""
    anonymizer = DataAnonymizer(master_seed=12345)
    
    valor = "1234567890"
    masked = anonymizer.mask(valor, mask_char="*", visible_chars=4)
    
    assert masked == "******7890", "Debe enmascarar correctamente"
    assert len(masked) == len(valor), "Longitud debe mantenerse"
    print("✓ Test enmascaramiento: PASS")


def test_hash_method():
    """Test de hash"""
    anonymizer = DataAnonymizer(master_seed=12345)
    
    valor = "dato_sensible"
    hashed = anonymizer.hash(valor)
    
    assert len(hashed) == 64, "Hash SHA-256 debe tener 64 caracteres"
    assert hashed != valor, "Hash debe ser diferente al valor original"
    
    # Mismo valor debe producir mismo hash
    hashed2 = anonymizer.hash(valor)
    assert hashed == hashed2, "Hash debe ser determinístico"
    print("✓ Test hash: PASS")


def test_generalize():
    """Test de generalización"""
    anonymizer = DataAnonymizer(master_seed=12345)
    
    # Generalización de edad con precisión 10
    edad = 25
    generalized = anonymizer.generalize(edad, precision=10)
    assert generalized == "20-30", f"Debe generalizar a rango 20-30, obtuvo {generalized}"
    
    # Otra prueba
    edad2 = 35
    generalized2 = anonymizer.generalize(edad2, precision=10)
    assert generalized2 == "30-40", f"Debe generalizar a rango 30-40, obtuvo {generalized2}"
    print("✓ Test generalización: PASS")


def test_different_seeds():
    """Test con diferentes seeds produce diferentes resultados"""
    anonymizer1 = DataAnonymizer(master_seed=111)
    anonymizer2 = DataAnonymizer(master_seed=222)
    
    valor = "dato_test"
    result1 = anonymizer1.pseudonymize(valor, "generico")
    result2 = anonymizer2.pseudonymize(valor, "generico")
    
    assert result1 != result2, "Seeds diferentes deben producir resultados diferentes"
    print("✓ Test diferentes seeds: PASS")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJECUTANDO TESTS DE ANONIMIZADOR")
    print("="*60 + "\n")
    
    try:
        test_pseudonymize_deterministic()
        test_pseudonymize_cedula()
        test_pseudonymize_email()
        test_pseudonymize_telefono()
        test_mask()
        test_hash_method()
        test_generalize()
        test_different_seeds()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*60 + "\n")
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        sys.exit(1)
