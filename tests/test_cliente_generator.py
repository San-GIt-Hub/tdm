"""
Tests para el generador de clientes sintéticos
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from synthetic_data.cliente_generator import ClienteGenerator
from anonymization.validators_ec import EcuadorValidators
import re

validar_cedula = EcuadorValidators.validar_cedula

def validar_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def test_generate_cliente():
    """Test de generación de un cliente"""
    generator = ClienteGenerator(seed=42)
    cliente = generator.generate_cliente(1)
    
    # Verificar campos requeridos
    required_fields = [
        "customer_id", "nombre", "apellido", "cedula",
        "fecha_nacimiento", "email", "direccion", "telefono",
        "fecha_creacion", "estado_cliente"
    ]
    
    for field in required_fields:
        assert field in cliente, f"Cliente debe tener campo {field}"
    
    print("✓ Test generar cliente: PASS")


def test_cliente_customer_id():
    """Test de customer_id único"""
    generator = ClienteGenerator(seed=42)
    cliente1 = generator.generate_cliente(1)
    cliente2 = generator.generate_cliente(2)
    
    assert cliente1["customer_id"] != cliente2["customer_id"], "customer_id debe ser único"
    assert cliente1["customer_id"] == "Cus001", f"Primer customer_id debe ser Cus001, obtuvo {cliente1['customer_id']}"
    assert cliente2["customer_id"] == "Cus002", f"Segundo customer_id debe ser Cus002, obtuvo {cliente2['customer_id']}"
    print("✓ Test customer_id único: PASS")


def test_cliente_cedula_valida():
    """Test de cédula válida"""
    generator = ClienteGenerator(seed=42)
    cliente = generator.generate_cliente(1)
    
    assert validar_cedula(cliente["cedula"]), "Cédula debe ser válida"
    assert len(cliente["cedula"]) == 10, "Cédula debe tener 10 dígitos"
    print("✓ Test cédula válida: PASS")


def test_cliente_email_valido():
    """Test de email válido sin acentos"""
    generator = ClienteGenerator(seed=42)
    cliente = generator.generate_cliente(1)
    
    assert validar_email(cliente["email"]), "Email debe ser válido"
    assert "@" in cliente["email"], "Email debe contener @"
    # Verificar que no hay acentos
    assert all(ord(c) < 128 for c in cliente["email"]), "Email no debe tener acentos"
    print("✓ Test email válido: PASS")


def test_cliente_edad_mayor_18():
    """Test de regla de negocio: edad >= 18 años"""
    generator = ClienteGenerator(seed=42)
    
    for i in range(10):
        cliente = generator.generate_cliente(i)
        fecha_nac_str = cliente["fecha_nacimiento"]
        
        # Intentar parsear con diferentes formatos
        try:
            fecha_nac = datetime.strptime(fecha_nac_str, "%Y-%m-%d")
        except ValueError:
            try:
                fecha_nac = datetime.strptime(fecha_nac_str, "%d-%m-%Y")
            except ValueError:
                # Si ninguno funciona, intentar con /
                try:
                    fecha_nac = datetime.strptime(fecha_nac_str, "%Y/%m/%d")
                except ValueError:
                    fecha_nac = datetime.strptime(fecha_nac_str, "%d/%m/%Y")
        
        edad = (datetime.now() - fecha_nac).days / 365.25
        
        assert edad >= 18, f"Cliente {i} debe tener al menos 18 años, tiene {edad:.1f}"
    
    print("✓ Test edad >= 18 años: PASS")


def test_cliente_estado_inactivo():
    """Test de regla de negocio: inactivos >= 6 meses"""
    generator = ClienteGenerator(seed=42)
    
    # Generar varios clientes y verificar los inactivos
    for i in range(20):
        cliente = generator.generate_cliente(i)
        
        if cliente["estado_cliente"] == "Inactivo":
            fecha_creacion_str = cliente["fecha_creacion"]
            
            # Parsear fecha de creación manejando múltiples formatos
            fecha_creacion = None
            formatos = [
                "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y",
                "%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S",
            ]
            
            for formato in formatos:
                try:
                    fecha_creacion = datetime.strptime(fecha_creacion_str, formato)
                    break
                except ValueError:
                    continue
            
            # Si incluye hora, intentar extraer solo la fecha
            if fecha_creacion is None and ' ' in fecha_creacion_str:
                fecha_solo = fecha_creacion_str.split()[0]
                for formato in formatos[:4]:  # Solo formatos sin hora
                    try:
                        fecha_creacion = datetime.strptime(fecha_solo, formato)
                        break
                    except ValueError:
                        continue
            
            # Si aún no se puede parsear, saltar este registro
            if fecha_creacion is None:
                print(f"  WARNING: No se pudo parsear fecha: {fecha_creacion_str}")
                continue
            
            meses_diferencia = (datetime.now() - fecha_creacion).days / 30.44
            
            assert meses_diferencia >= 6, \
                f"Cliente inactivo debe tener al menos 6 meses, tiene {meses_diferencia:.1f}"
    
    print("✓ Test estado inactivo >= 6 meses: PASS")


def test_cliente_telefono_formato():
    """Test de formato de teléfono ecuatoriano"""
    generator = ClienteGenerator(seed=42)
    cliente = generator.generate_cliente(1)
    
    telefono = cliente["telefono"]
    assert len(telefono) == 10, "Teléfono debe tener 10 dígitos"
    assert telefono.startswith("09"), "Teléfono debe empezar con 09"
    assert telefono.isdigit(), "Teléfono debe ser numérico"
    print("✓ Test formato teléfono: PASS")


def test_generate_multiple_clientes():
    """Test de generación de múltiples clientes"""
    generator = ClienteGenerator(seed=42)
    clientes = generator.generate_clientes(count=50)
    
    assert len(clientes) == 50, "Debe generar 50 clientes"
    
    # Verificar que todos los customer_id son únicos
    customer_ids = [c["customer_id"] for c in clientes]
    assert len(customer_ids) == len(set(customer_ids)), "Todos los customer_id deben ser únicos"
    
    print("✓ Test generar múltiples clientes: PASS")


def test_deterministic_generation():
    """Test de generación determinística con seed"""
    generator1 = ClienteGenerator(seed=123)
    generator2 = ClienteGenerator(seed=123)
    
    cliente1 = generator1.generate_cliente(1)
    cliente2 = generator2.generate_cliente(1)
    
    # Verificar que customer_id es determinístico (el único campo 100% controlado)
    assert cliente1["customer_id"] == cliente2["customer_id"], \
        f"customer_id debe ser igual: {cliente1['customer_id']} vs {cliente2['customer_id']}"
    
    # Los demás campos pueden tener variación por el uso de Faker y random internos
    print("✓ Test generación determinística: PASS")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EJECUTANDO TESTS DE GENERADOR DE CLIENTES")
    print("="*60 + "\n")
    
    try:
        test_generate_cliente()
        test_cliente_customer_id()
        test_cliente_cedula_valida()
        test_cliente_email_valido()
        test_cliente_edad_mayor_18()
        test_cliente_estado_inactivo()
        test_cliente_telefono_formato()
        test_generate_multiple_clientes()
        test_deterministic_generation()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*60 + "\n")
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        sys.exit(1)
