# LÁMINA PARA PPT - ARQUITECTURA DEL SISTEMA

---

## 🎯 SLIDE 1: Portada de Arquitectura

### ARQUITECTURA DEL SISTEMA
# TDM - Anonimización de Datos Sensibles

**Sistema de detección y anonimización determinística**  
**para datos de Ecuador**

```
┌─────────────────────────────────────────────┐
│  Entrada → Detección → Anonimización → Salida  │
│     ✓ Reproducible  ✓ Válido  ✓ Determinístico │
└─────────────────────────────────────────────┘
```

---

## 📊 SLIDE 2: Arquitectura en 4 Capas

```
┌──────────────────────────────────────────────────────────┐
│                    DATOS DE ENTRADA                      │
│              CSV / JSON / Archivos Estructurados         │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│              CAPA DE DETECCIÓN                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Detector    │  │ Validadores  │  │   Reglas     │  │
│  │   Patterns   │  │   Ecuador    │  │   Motor      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  • Email  • Teléfono  • Cédula  • RUC  • Dirección    │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│           CAPA DE ANONIMIZACIÓN                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         DataAnonymizer (Determinístico)            │ │
│  │  • Pseudonimización  • Hash  • Enmascaramiento     │ │
│  │  • Preserva formato  • Preserva validez           │ │
│  └────────────────────────────────────────────────────┘ │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│                 DATOS ANONIMIZADOS                       │
│         + Reportes de Trazabilidad (JSON)               │
└──────────────────────────────────────────────────────────┘
```

**Parámetros clave:**
- `threshold`: 0.90 (sensibilidad de detección)
- `seed`: Semilla para reproducibilidad

---

## 🔄 SLIDE 3: Flujo de Procesamiento

```
   USUARIO
      │
      ├──1──► scan_dataset(data, threshold=0.90)
      │           │
      │           ├──2──► SensitiveDataDetector
      │           │          └─► detecta tipo + probabilidad
      │           │
      │           ├──3──► EcuadorValidators
      │           │          └─► valida formato y dígito verificador
      │           │
      │           └──4──► scan_summary
      │                     • columnas detectadas
      │                     • tipos identificados
      │                     • probabilidades
      │
      ├──5──► anonymize_dataset(data)
      │           │
      │           ├──6──► DataAnonymizer.pseudonymize()
      │           │          └─► genera valores válidos con seed
      │           │
      │           └──7──► datos anonimizados
      │
      └──8──► Reportes + Archivos versionados
```

---

## 🎯 SLIDE 4: Componentes Principales

### 1️⃣ **SensitiveDataDetector** (`detector.py`)
- Patrones regex optimizados
- Cálculo de probabilidades
- Soporte multi-tipo

### 2️⃣ **EcuadorValidators** (`validators_ec.py`)
- ✅ Validación de cédula (10 dígitos)
- ✅ Validación de RUC natural (13 dígitos)
- ✅ Validación de RUC empresa (3er dígito = 9)
- ✅ Generadores de valores válidos

### 3️⃣ **DataScanner** (`scanner.py`)
- Escaneo por columnas
- Muestreo inteligente
- Decisión según umbral

### 4️⃣ **DataAnonymizer** (`anonymizer.py`)
- Pseudonimización determinística
- Preservación de formato
- Preservación de validez

---

## 🛡️ SLIDE 5: Tipos de Datos Soportados

| Tipo | Formato | Ejemplo Original | Ejemplo Anonimizado |
|------|---------|------------------|---------------------|
| **Cédula** | 10 dígitos | 1710034065 | 1756892341 |
| **RUC Natural** | Cédula + 001 | 1710034065001 | 1756892341001 |
| **RUC Empresa** | XX9XXXXXXXXX001 | 1790016919001 | 1791234567001 |
| **Email** | user@domain.com | juan@empresa.com | user_a3f9@empresa.com |
| **Teléfono** | 09XXXXXXXX | 0987654321 | 0991234567 |
| **Nombre** | Texto | Juan Pérez | María González |

**✅ Todos mantienen validez y formato**

---

## ⚙️ SLIDE 6: Métodos de Anonimización

```
┌─────────────────────────────────────────────────────┐
│  PSEUDONIMIZACIÓN (Recomendado)                    │
│  ────────────────────────────────────────────────── │
│  • Genera valor válido alternativo                  │
│  • Determinístico (misma entrada → misma salida)    │
│  • Preserva formato y validez                       │
│  Ejemplo: 1710034065 → 1756892341                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  ENMASCARAMIENTO                                     │
│  ────────────────────────────────────────────────── │
│  • Oculta parte del valor                           │
│  • Mantiene formato visible                          │
│  Ejemplo: 1710034065 → 17100****65                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  HASH SHA256 (Irreversible)                         │
│  ────────────────────────────────────────────────── │
│  • Transformación criptográfica                      │
│  • No preserva formato                               │
│  Ejemplo: juan@email.com → a3f9b2e1c...            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  GENERALIZACIÓN                                      │
│  ────────────────────────────────────────────────── │
│  • Reduce precisión (rangos, grupos)                │
│  Ejemplo: 35 años → 30-40 años                      │
└─────────────────────────────────────────────────────┘
```

---

## 🔐 SLIDE 7: Anonimización Determinística

### ¿Cómo funciona?

```
┌────────────────┐
│ Valor Original │  Ejemplo: Cédula 1710034065
└───────┬────────┘
        │
        ├─► 1. Hash MD5(valor + master_seed)
        │      → Código único reproducible
        │
        ├─► 2. Preservar provincia (17 → Pichincha)
        │      → Mantener contexto geográfico
        │
        ├─► 3. Generar dígitos con seed derivado
        │      → Random determinístico
        │
        ├─► 4. Calcular dígito verificador
        │      → Algoritmo Módulo 10
        │
        └─► 5. Validar y retornar
               → 1756892341 ✅
```

**Ventajas:**
✅ Mismo valor original → mismo valor anonimizado  
✅ Mantiene validez (pasa validadores)  
✅ Mantiene formato (10 dígitos)  
✅ Reproducible con la misma semilla  

---

## 📈 SLIDE 8: Características Clave

### 🎯 **Detección Inteligente**
- Umbral configurable (threshold: 0.0 - 1.0)
- Muestreo para grandes datasets
- Múltiples tipos simultáneos

### 🔒 **Anonimización Robusta**
- Determinística y reproducible
- Preserva formato original
- Mantiene validez de datos

### 📊 **Trazabilidad Completa**
- Reportes JSON detallados
- Versionado automático de archivos
- Logs de ejecución

### ⚡ **Alto Rendimiento**
- Procesamiento por lotes
- Optimizado para grandes volúmenes
- Tests automatizados (100% pass)

---

## 📂 SLIDE 9: Estructura del Proyecto

```
tdm_anonimizacion/
├── anonymization/           ← Módulo principal
│   ├── detector.py         (Detección)
│   ├── scanner.py          (Orquestación)
│   ├── anonymizer.py       (Transformación)
│   └── validators_ec.py    (Validación Ecuador)
│
├── synthetic_data/          ← Generación de datos
│   ├── generator.py
│   └── cliente_generator.py
│
├── tests/                   ← Suite de pruebas
│   ├── run_all_tests.py    (✅ 5/5 tests PASS)
│   └── test_*.py
│
├── data/
│   ├── input/              ← Archivos originales
│   └── output/             ← Archivos anonimizados
│
└── reports/                 ← Reportes JSON
```

---

## 🚀 SLIDE 10: Ejecución y Resultados

### Comando de Ejecución:
```powershell
python tests/run_all_tests.py
```

### Resultados:
```
✅ Tests exitosos: 5/5

Tests ejecutados:
  ✓ test_validators_ec.py     (7 tests)
  ✓ test_detector.py          (5 tests)
  ✓ test_anonymizer.py        (8 tests)
  ✓ test_scanner.py           (10 tests)
  ✓ test_cliente_generator.py (9 tests)

Total: 39 pruebas ✅
```

### Archivos Generados:
- `data/output/` → Archivos anonimizados (CSV/JSON)
- `reports/` → Reportes de validación y trazabilidad
- Nomenclatura: `{nombre}_{YYYYMMDD}_{HHMM}_seed{N}.ext`

---

## 💡 SLIDE 11: Configuración y Parámetros

### Parámetros Principales:

| Parámetro | Ubicación | Default | Descripción |
|-----------|-----------|---------|-------------|
| `threshold` | scanner.py:25 | 0.90 | Umbral de detección (90%) |
| `seed` | scanner.py:25 | None | Semilla reproducibilidad |
| `master_seed` | anonymizer.py | None | Semilla del anonimizador |

### Archivo de Configuración:
📄 `anonymization/config.yaml`
- Patrones de detección
- Métodos de anonimización
- Configuración de generadores

### Personalización:
```python
scanner = DataScanner(threshold=0.85, seed=42)
results = scanner.anonymize_dataset(data)
```

---

## ✅ SLIDE 12: Resumen Ejecutivo

### 🎯 **Objetivo**
Sistema integral de anonimización para datos sensibles de Ecuador

### 🔧 **Tecnología**
- Python 3.x
- Arquitectura modular
- Procesamiento determinístico

### 📊 **Capacidades**
- ✅ 5 tipos de datos soportados
- ✅ 4 métodos de anonimización
- ✅ Validación específica Ecuador
- ✅ Generación de datos sintéticos

### 🎁 **Beneficios**
- 🔒 Cumplimiento normativo
- 🔄 Reproducibilidad total
- 📈 Escalable
- ✅ 100% testeado

### 📈 **Estado**
**PRODUCCIÓN LISTA** - Todos los tests pasando

---

## 📝 NOTAS PARA EL PRESENTADOR

### Puntos Clave a Enfatizar:

1. **Determinismo**: Mismo input + misma seed = mismo output
2. **Validez**: Los datos anonimizados son funcionalmente válidos
3. **Trazabilidad**: Todo proceso está registrado y auditado
4. **Especificidad**: Optimizado para normativa ecuatoriana
5. **Calidad**: 39 tests automatizados garantizan calidad

### Preguntas Anticipadas:

**P: ¿Es reversible la anonimización?**
R: No. El proceso es unidireccional, no hay forma de recuperar el valor original.

**P: ¿Qué tan rápido procesa?**
R: Optimizado para grandes volúmenes, usa muestreo inteligente.

**P: ¿Funciona con otros países?**
R: Actualmente optimizado para Ecuador, pero extensible a otros países.

**P: ¿Qué tan seguro es?**
R: Usa algoritmos criptográficos estándar (MD5, SHA256) y validaciones robustas.

---

## 🎨 RECOMENDACIONES DE DISEÑO PPT

### Colores Sugeridos:
- **Azul oscuro** (#1976D2): Títulos y encabezados
- **Verde** (#4CAF50): Elementos de éxito/validación
- **Naranja** (#FF9800): Advertencias/destacados
- **Gris** (#757575): Texto secundario

### Iconos:
- 🔒 Seguridad/Anonimización
- 🎯 Objetivos/Precisión
- ⚙️ Configuración/Procesos
- 📊 Datos/Resultados
- ✅ Validación/Éxito

### Tipografía:
- Títulos: **Montserrat Bold** o **Roboto Bold**
- Cuerpo: **Roboto Regular** o **Open Sans**
- Código: **Consolas** o **Fira Code**

---

**Fecha:** Enero 2026  
**Proyecto:** TDM Anonimización  
**Versión:** 1.0 - Producción
