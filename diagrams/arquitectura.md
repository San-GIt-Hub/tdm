# Diagrama de Arquitectura - TDM Anonimización

## Arquitectura del Sistema

```mermaid
graph TB
    subgraph "Capa de Entrada"
        INPUT[Datos de Entrada<br/>CSV/JSON]
        CONFIG[Configuración<br/>config.yaml]
    end
    
    subgraph "Capa de Detección"
        DETECTOR[SensitiveDataDetector<br/>detector.py]
        VALIDATOR[EcuadorValidators<br/>validators_ec.py]
        RULES[RuleEngine<br/>rules.py]
    end
    
    subgraph "Capa de Escaneo"
        SCANNER[DataScanner<br/>scanner.py]
        DETECTOR --> SCANNER
        VALIDATOR --> SCANNER
    end
    
    subgraph "Capa de Anonimización"
        ANONYMIZER[DataAnonymizer<br/>anonymizer.py]
        SCANNER --> ANONYMIZER
        RULES --> ANONYMIZER
    end
    
    subgraph "Capa de Salida"
        OUTPUT[Datos Anonimizados<br/>CSV/JSON]
        REPORTS[Reportes<br/>JSON/TXT]
    end
    
    INPUT --> SCANNER
    CONFIG --> SCANNER
    ANONYMIZER --> OUTPUT
    SCANNER --> REPORTS
    ANONYMIZER --> REPORTS
    
    style DETECTOR fill:#e1f5ff
    style VALIDATOR fill:#e1f5ff
    style SCANNER fill:#fff4e1
    style ANONYMIZER fill:#ffe1e1
    style OUTPUT fill:#e1ffe1
    style REPORTS fill:#e1ffe1
```

## Flujo de Procesamiento

```mermaid
sequenceDiagram
    participant User
    participant Scanner as DataScanner
    participant Detector as SensitiveDataDetector
    participant Validator as EcuadorValidators
    participant Anonymizer as DataAnonymizer
    participant Output as Archivos de Salida
    
    User->>Scanner: 1. scan_dataset(data, threshold=0.90)
    Scanner->>Detector: 2. detect_type(value)
    Detector->>Validator: 3. validar_cedula/ruc/etc(value)
    Validator-->>Detector: 4. ✓ Es válido
    Detector-->>Scanner: 5. Tipo detectado + probabilidad
    Scanner-->>User: 6. scan_summary
    
    User->>Scanner: 7. anonymize_dataset(data)
    Scanner->>Anonymizer: 8. pseudonymize(value, type, seed)
    Anonymizer->>Validator: 9. generar_cedula/ruc_valida()
    Validator-->>Anonymizer: 10. Nuevo valor válido
    Anonymizer-->>Scanner: 11. Valor anonimizado
    Scanner->>Output: 12. Guardar resultados
    Scanner-->>User: 13. Reporte de anonimización
```

## Componentes y Responsabilidades

```mermaid
graph LR
    subgraph "anonymization/"
        D[detector.py<br/>━━━━━━━━<br/>• Patrones regex<br/>• Validación de formato<br/>• Cálculo de probabilidades]
        V[validators_ec.py<br/>━━━━━━━━<br/>• Validador de cédula<br/>• Validador de RUC<br/>• Generadores válidos]
        S[scanner.py<br/>━━━━━━━━<br/>• Escaneo por columna<br/>• Muestreo de datos<br/>• Decisión según umbral]
        A[anonymizer.py<br/>━━━━━━━━<br/>• Pseudonimización<br/>• Enmascaramiento<br/>• Hash determinístico]
        R[rules.py<br/>━━━━━━━━<br/>• Reglas de transformación<br/>• Motor de reglas]
    end
    
    D --> S
    V --> D
    V --> A
    R --> A
    S --> A
    
    style D fill:#bbdefb
    style V fill:#c8e6c9
    style S fill:#fff9c4
    style A fill:#ffccbc
    style R fill:#f8bbd0
```

## Tipos de Datos Soportados

```mermaid
mindmap
  root((TDM<br/>Anonimización))
    Identificadores
      Cédula Ecuador
        10 dígitos
        Algoritmo Módulo 10
      RUC Natural
        13 dígitos
        Termina en 001
      RUC Empresa
        13 dígitos
        3er dígito = 9
    Contacto
      Email
        Formato RFC 5322
      Teléfono
        10 dígitos
        Inicia 09
    Personal
      Nombre
      Dirección
      Edad
```

## Estructura de Directorios

```
tdm_anonimizacion/
│
├── anonymization/          # Módulo principal
│   ├── __init__.py        # Exporta clases principales
│   ├── detector.py        # Detección de datos sensibles
│   ├── scanner.py         # Escaneo y orquestación
│   ├── anonymizer.py      # Anonimización determinística
│   ├── validators_ec.py   # Validadores de Ecuador
│   ├── rules.py           # Motor de reglas
│   └── config.yaml        # Configuración global
│
├── synthetic_data/         # Generación de datos sintéticos
│   ├── generator.py       # Generador base
│   ├── cliente_generator.py  # Generador de clientes
│   ├── validator.py       # Validadores de calidad
│   ├── profiler.py        # Perfilado de datos
│   └── fault_injector.py  # Inyección de errores
│
├── tests/                  # Suite de pruebas
│   ├── run_all_tests.py   # Ejecutor principal
│   ├── test_detector.py   # Tests de detección
│   ├── test_scanner.py    # Tests de escaneo
│   ├── test_anonymizer.py # Tests de anonimización
│   └── test_validators_ec.py  # Tests de validadores
│
├── data/                   # Datos de entrada/salida
│   ├── input/             # Archivos originales
│   └── output/            # Archivos procesados
│
├── reports/                # Reportes generados
├── examples/               # Ejemplos de uso
└── docs/                   # Documentación
```

## Parámetros Configurables

| Parámetro | Ubicación | Valor por Defecto | Descripción |
|-----------|-----------|-------------------|-------------|
| `threshold` | scanner.py L25 | 0.90 | Umbral de probabilidad (0.0-1.0) |
| `seed` | scanner.py L25 | None | Semilla para reproducibilidad |
| `master_seed` | anonymizer.py | None | Semilla maestra del anonimizador |
| `patterns` | config.yaml L8-26 | Varios | Patrones de detección regex |
| `default_method` | config.yaml L30 | pseudonymize | Método de anonimización por defecto |

## Métodos de Anonimización

```mermaid
graph TD
    A[Valor Original] --> B{Método}
    B -->|pseudonymize| C[Pseudónimo Válido<br/>Determinístico]
    B -->|mask| D[Enmascaramiento<br/>Parcial]
    B -->|hash| E[Hash SHA256<br/>Irreversible]
    B -->|generalize| F[Generalización<br/>Rangos/Grupos]
    
    C --> G[Preserva Formato ✓<br/>Preserva Validez ✓<br/>Reproducible ✓]
    D --> H[Preserva Formato ✓<br/>Preserva Validez ✗<br/>Reproducible ✓]
    E --> I[Preserva Formato ✗<br/>Preserva Validez ✗<br/>Reproducible ✓]
    F --> J[Preserva Formato ✗<br/>Preserva Validez ~<br/>Reproducible ✓]
    
    style C fill:#c8e6c9
    style D fill:#fff9c4
    style E fill:#ffccbc
    style F fill:#e1bee7
```

## Flujo de Anonimización Determinística

```mermaid
flowchart LR
    A[Valor Original<br/>1710034065] --> B[Hash MD5<br/>con Master Seed]
    B --> C[Código de Provincia<br/>17 → Pichincha]
    C --> D[Generar Dígitos<br/>con Seed Derivado]
    D --> E[Calcular<br/>Dígito Verificador]
    E --> F[Valor Anonimizado<br/>1756789043]
    
    F --> G{¿Válido?}
    G -->|Sí| H[✓ Retornar]
    G -->|No| D
    
    style A fill:#bbdefb
    style F fill:#c8e6c9
    style H fill:#a5d6a7
```

