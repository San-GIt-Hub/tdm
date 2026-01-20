# TDM Anonimización y Datos Sintéticos

Sistema completo de Test Data Management (TDM) que implementa dos desafíos principales:
1. **Anonimización determinística** de datos sensibles con detección probabilística
2. **Generación de datos sintéticos** con inyección controlada de fallas y validación determinística

## 📋 Descripción

Este proyecto cumple con los requisitos de ambos desafíos técnicos para el rol de Coordinador TDM, proporcionando:

### Desafío de Anonimización
- ✅ Escaneo e identificación de datos sensibles (cédula, RUC, teléfono, email)
- ✅ Detección probabilística con umbral configurable (90% por defecto)
- ✅ Anonimización determinística basada en semilla
- ✅ Preservación de formato y validez de datos
- ✅ Integridad referencial entre entornos

### Desafío de Datos Sintéticos
- ✅ Generación de 100-500 registros de clientes (parametrizable)
- ✅ Inyección de fallas controlada (0.05% parametrizable)
- ✅ Tipos de fallas: schema, domain, dup, business
- ✅ Validación determinística contra contrato de datos
- ✅ Reportes completos de calidad y trazabilidad
- ✅ Salidas en CSV y JSON versionadas por fecha y seed

## 🏗️ Estructura del Proyecto

```
tdm_anonimizacion/
│
├── anonymization/              # Módulos de anonimización
│   ├── scanner.py             # Escaneo de datos sensibles
│   ├── detector.py            # Detección con probabilidades (NUEVO)
│   ├── anonymizer.py          # Anonimización determinística (NUEVO)
│   ├── rules.py               # Motor de reglas
│   ├── validators_ec.py       # Validadores ecuatorianos (NUEVO)
│   ├── config.yaml            # Configuración
│   └── demo_anonymization.py  # Script demo anonimización (NUEVO)
│
├── synthetic_data/             # Generación de datos sintéticos
│   ├── generator.py           # Generador genérico
│   ├── cliente_generator.py   # Generador de clientes (NUEVO)
│   ├── fault_injector.py      # Inyección de fallas (ACTUALIZADO)
│   ├── validator.py           # Validador genérico
│   ├── cliente_validator.py   # Validador de clientes (NUEVO)
│   ├── profiler.py            # Perfilado de datos
│   └── demo_synthetic_data.py # Script demo sintéticos (NUEVO)
│
├── data/                       # Directorio de datos
│   ├── input/                 # Datos de entrada
│   └── output/                # Datos procesados
│
├── reports/                   # Reportes generados
├── diagrams/                  # Diagramas del sistema
├── venv/                      # Entorno virtual
├── README.md                  # Este archivo
└── requirements.txt           # Dependencias
```

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd tdm_anonimizacion
```

### 2. Crear y activar el entorno virtual

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 📊 Uso - Desafío de Datos Sintéticos

### Ejecución Rápida
```bash
cd synthetic_data
python demo_synthetic_data.py
```

### Ejemplo Programático
```python
from synthetic_data.cliente_generator import ClienteGenerator
from synthetic_data.fault_injector import FaultInjector
from synthetic_data.cliente_validator import ClienteValidator

# 1. Generar clientes
generator = ClienteGenerator(locale='es_ES', seed=42)
clientes = generator.generate_clientes(count=100)

# 2. Inyectar fallas (0.05% = 0.0005)
injector = FaultInjector(fault_rate=0.0005, seed=42)
clientes_con_errores, log = injector.inject_faults(clientes)

# 3. Validar
validator = ClienteValidator()
reporte = validator.validate_dataset(clientes_con_errores)

print(f"Cumplimiento: {reporte['porcentaje_cumplimiento']}%")
```

### Campos Generados
- `customer_id`: Identificador único (Cus001, Cus002, ...)
- `nombre`: Nombre sintético
- `apellido`: Apellido sintético
- `cedula`: Cédula ecuatoriana válida
- `fecha_nacimiento`: Fecha en formato dd-mm-yyyy (18-90 años)
- `email`: Email coherente con nombre
- `direccion`: Dirección sintética
- `telefono`: Teléfono ecuatoriano (09XXXXXXXX)
- `fecha_creacion`: Timestamp dd/mm/yyyy HH:MM:SS
- `estado_cliente`: Activo o Inactivo

### Reglas de Negocio Implementadas
1. **Regla 1**: Edad ≥ 18 años
2. **Regla 2**: Si estado=Inactivo → fecha_creacion ≥ 6 meses
3. **Regla 3**: Email con formato válido
4. **Regla 4**: customer_id único
5. **Regla 5**: Sin valores nulos

### Tipos de Fallas Inyectadas
- **schema**: Tipos de dato, formatos, valores nulos
- **domain**: Valores fuera del dominio permitido
- **dup**: Duplicados (violación de unicidad)
- **business**: Violación de reglas de negocio

### Archivos Generados
```
data/output/clientes_<timestamp>_seed<N>.json     # Dataset en JSON
data/output/clientes_<timestamp>_seed<N>.csv      # Dataset en CSV
reports/validation_report_<timestamp>_seed<N>.json # Reporte de validación
reports/injection_log_<timestamp>_seed<N>.json    # Log de inyección
```

## 🔒 Uso - Desafío de Anonimización

### Ejecución Rápida
```bash
cd anonymization
python demo_anonymization.py
```

### Ejemplo Programático
```python
from anonymization.detector import SensitiveDataDetector
from anonymization.anonymizer import DataAnonymizer
from anonymization.rules import AnonymizationRule, RuleEngine

# 1. Escanear y detectar (umbral 90%)
detector = SensitiveDataDetector(threshold=0.90)
scan_results = detector.scan_dataset(datos)

# 2. Crear reglas automáticamente
engine = RuleEngine()
for columna, resultado in scan_results.items():
    if resultado['requires_anonymization']:
        regla = AnonymizationRule(
            field_name=columna,
            data_type=resultado['type'],
            method='pseudonymize'
        )
        engine.add_rule(regla)

# 3. Anonimizar determinísticamente
anonymizer = DataAnonymizer(locale='es_ES', master_seed=12345)
datos_anonimizados = anonymizer.anonymize_dataset(datos, engine)
```

### Tipos de Datos Detectados
- **cedula**: Cédula ecuatoriana (10 dígitos con validación)
- **ruc_natural**: RUC persona natural (13 dígitos)
- **ruc_empresa**: RUC empresa (tercer dígito = 9)
- **telefono**: Teléfono ecuatoriano (09XXXXXXXX)
- **email**: Correo electrónico

### Técnicas de Anonimización
1. **Pseudonimización**: Reemplaza con datos sintéticos válidos y determinísticos
2. **Enmascaramiento**: Oculta parcialmente los datos (****1234)
3. **Hashing**: Aplica funciones hash criptográficas
4. **Generalización**: Reduce precisión de datos numéricos

### Características Clave
- ✅ **Determinismo**: Misma semilla → mismo resultado
- ✅ **Formato preservado**: Longitud y estructura mantenidas
- ✅ **Validez**: Datos anonimizados pasan validaciones (cédulas válidas)
- ✅ **Integridad referencial**: Correlación entre ejecuciones

## 🧪 Validadores Ecuatorianos

### Cédula
```python
from anonymization.validators_ec import EcuadorValidators

validator = EcuadorValidators()

# Validar
es_valida = validator.validar_cedula('1713456789')

# Generar
cedula = validator.generar_cedula_valida(provincia=17)
```

### RUC Natural y Empresa
```python
# RUC Natural (cédula + 001)
ruc_nat = validator.generar_ruc_natural(provincia=9)
es_valido = validator.validar_ruc_natural(ruc_nat)

# RUC Empresa (tercer dígito = 9)
ruc_emp = validator.generar_ruc_empresa(provincia=17)
es_valido = validator.validar_ruc_empresa(ruc_emp)
```

## 📈 Reportes y Trazabilidad

### Reporte de Validación (Sintéticos)
```json
{
  "total_registros": 100,
  "errores_totales": 5,
  "porcentaje_cumplimiento": 95.0,
  "errores_por_tipo": {
    "schema": 1,
    "domain": 2,
    "dup": 1,
    "business": 1
  },
  "muestras_de_errores": {...}
}
```

### Reporte de Anonimización
```json
{
  "timestamp": "20260118_1530",
  "seed": 12345,
  "threshold": 0.90,
  "columns_requiring_anonymization": 5,
  "scan_results": {
    "cedula": {
      "type": "cedula",
      "probability": 1.0,
      "requires_anonymization": true
    }
  }
}
```

## ⚙️ Configuración

### Parámetros Principales

**Datos Sintéticos:**
```python
SEED = 42                    # Semilla para reproducibilidad
NUM_CLIENTES = 100           # 100-500 clientes
FAULT_RATE = 0.0005         # 0.05% de errores
```

**Anonimización:**
```python
SEED = 12345                 # Semilla maestra
THRESHOLD = 0.90            # Umbral de detección (90%)
```

### Archivo de Configuración
Edita `anonymization/config.yaml` para ajustes globales.

## 🔧 Dependencias

```
faker>=40.0.0       # Generación de datos sintéticos
pyyaml>=6.0.0       # Lectura de configuración
```

## 📝 Entregables del Proyecto

- ✅ **Repositorio Git**: Código fuente versionado
- ✅ **README**: Instrucciones completas (este archivo)
- ✅ **Solución funcional**: Scripts ejecutables y módulos
- ✅ **Dataset de ejemplo**: Generadores incluidos
- ⏳ **Arquitectura**: Diagramas en `/diagrams`
- ⏳ **Presentación**: PDF/PPTX para foro técnico

## 🎯 Casos de Uso

### 1. Generar dataset de prueba limpio
```bash
cd synthetic_data
python -c "
from cliente_generator import ClienteGenerator
gen = ClienteGenerator(seed=42)
clientes = gen.generate_clientes(500)
print(f'Generados {len(clientes)} clientes')
"
```

### 2. Anonimizar base de datos existente
```python
# Cargar datos reales
import pandas as pd
df = pd.read_csv('clientes_produccion.csv')
datos = df.to_dict('records')

# Anonimizar
from anonymization.detector import SensitiveDataDetector
from anonymization.anonymizer import DataAnonymizer
from anonymization.rules import RuleEngine

detector = SensitiveDataDetector(threshold=0.90)
scan = detector.scan_dataset(datos)
# ... aplicar anonimización
```

### 3. Validar calidad de datos importados
```python
from synthetic_data.cliente_validator import ClienteValidator

validator = ClienteValidator()
reporte = validator.validate_dataset(datos_importados)

if reporte['porcentaje_cumplimiento'] < 95:
    print("⚠️ Datos no cumplen estándar de calidad")
```

## 🧪 Testing

### Ejecutar demo completo
```bash
# Demo de datos sintéticos
cd synthetic_data
python demo_synthetic_data.py

# Demo de anonimización
cd anonymization
python demo_anonymization.py
```

### Verificar determinismo
```python
# Dos ejecuciones con misma semilla deben dar mismo resultado
from cliente_generator import ClienteGenerator

gen1 = ClienteGenerator(seed=42)
gen2 = ClienteGenerator(seed=42)

c1 = gen1.generate_cliente(1)
c2 = gen2.generate_cliente(1)

assert c1 == c2, "No determinista!"
```

## 📧 Contacto

Para preguntas o sugerencias sobre este proyecto, por favor abre un issue en el repositorio.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

**Fecha de entrega**: 21 de enero de 2026, 21:00  
**Versión**: 1.0  
**Autor**: Candidato TDM
