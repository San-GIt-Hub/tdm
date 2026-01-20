# Guía de Inicio Rápido - TDM Anonimización

## ⚡ Instalación en 3 pasos

```bash
# 1. Clonar repositorio
git clone <url-del-repositorio>
cd tdm_anonimizacion

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt
```

## 🚀 Ejecutar Demos

### Demo de Datos Sintéticos
```bash
cd synthetic_data
python demo_synthetic_data.py
```

**Resultado esperado:**
- ✅ 100 clientes generados
- ✅ Fallas inyectadas (schema, domain, dup, business)
- ✅ Validación determinística
- ✅ Reportes en `reports/`
- ✅ Datasets en `data/output/`

### Demo de Anonimización
```bash
cd anonymization
python demo_anonymization.py
```

**Resultado esperado:**
- ✅ Escaneo de datos sensibles
- ✅ Detección probabilística (umbral 90%)
- ✅ Anonimización determinística
- ✅ Formato preservado
- ✅ Determinismo verificado

## 📊 Archivos Generados

Ambos demos generan archivos con timestamp y seed:

```
data/output/
├── clientes_<timestamp>_seed<N>.json
├── clientes_<timestamp>_seed<N>.csv
├── anonymization_<timestamp>_seed<N>_original.json
└── anonymization_<timestamp>_seed<N>_anonymized.json

reports/
├── validation_report_<timestamp>_seed<N>.json
├── injection_log_<timestamp>_seed<N>.json
└── anonymization_report_<timestamp>_seed<N>.json
```

## 🔧 Parámetros Configurables

### Datos Sintéticos
Editar en `synthetic_data/demo_synthetic_data.py`:
```python
SEED = 42                # Semilla
NUM_CLIENTES = 100       # Número de clientes (100-500)
FAULT_RATE = 0.0005     # Tasa de error (0.05%)
```

### Anonimización
Editar en `anonymization/demo_anonymization.py`:
```python
SEED = 12345            # Semilla maestra
THRESHOLD = 0.90        # Umbral de detección (90%)
```

## ✅ Verificación de Instalación

```bash
# Verificar Python
python --version  # Debe ser 3.8+

# Verificar pip
pip --version

# Verificar instalación de dependencias
pip list | findstr "faker\|pyyaml"  # Windows
pip list | grep -E "faker|pyyaml"   # Linux/Mac
```

## 🆘 Solución de Problemas

### Error: "No module named 'faker'"
```bash
pip install -r requirements.txt
```

### Error: PowerShell execution policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: Python no encontrado
Asegúrate de que Python 3.8+ está instalado y en el PATH.

## 📚 Siguiente Paso

Lee el [README.md](README.md) completo para documentación detallada.
