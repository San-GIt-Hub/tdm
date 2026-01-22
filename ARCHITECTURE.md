# Arquitectura del proyecto TDM Anonimizacion

## Visión general

Proyecto Python para detección y anonimización de datos sensibles (cédula, RUC, email, teléfono). Diseñado en capas: detectores (heurísticas y probabilidades), escaneo por columna (muestreo y probabilidades), orquestador de escaneo, y anonimizador determinístico que preserva formato y validez.

## Componentes principales

- `anonymization/`
  - `detector.py` — Reglas y heurísticas por tipo (email, teléfono, cédula, RUC). Devuelve puntuaciones/probabilidades por registro o por muestra.
  - `column_scanner.py` — Escaneo por columna: muestreo reproducible, conteo de coincidencias, cálculo de probabilidades por tipo, listas de valores coincidentes y decisión según umbral.
  - `scanner.py` — Orquestador que agrega resultados por columna y construye `scan_summary` y `decision_table` para decisiones de anonimización.
  - `anonymizer.py` — Anonimizador determinístico y preservador de formato; usa una semilla derivada del valor + master seed para producir pseudónimos reproducibles.

- `tests/`
  - `run_all_tests.py` — Runner principal: ejecuta la suite con el Python del `venv`, centraliza salida en `logs/ejecucion_<timestamp>.log`.
  - `test_scanner_identification.py` — Prueba para identificación por columna; genera muestras, imprime resumen y guarda `scan_summary_<timestamp>.json`.
  - Resto de tests: validadores (`test_validators_ec.py`), anonymizer, detector e integración (`test_scanner.py`, `test_anonymizer.py`, etc.).

- `logs/` — Carpeta de salida con `ejecucion_<timestamp>.log` y `scan_summary_<timestamp>.json` (artefactos de ejecución).

## Flujo de datos

1. El runner (`tests/run_all_tests.py`) carga los tests y ejecuta las funciones de escaneo/análisis usando el `venv`.
2. `scanner.scan_dataset()` utiliza `column_scanner.scan_dataset_columns()` para cada columna: toma una muestra, aplica `detector` y calcula probabilidades.
3. `scanner` consolida resultados en `scan_summary` y `decision_table` (tipo detectado, probabilidad, pasa umbral).
4. `anonymizer.pseudonymize()` se usa para verificar o transformar datos, garantizando reproducibilidad por semilla.
5. Resultados y diagnósticos se escriben en `logs/` como `.log` y JSONs para auditoría.

## Cómo ejecutar (rápido)

1. Activar el entorno virtual:

```powershell
& .\venv\Scripts\Activate.ps1
```

2. Ejecutar el runner de tests (usa el Python del `venv`):

```powershell
C:/PROYECTOS/tdm_anonimizacion/venv/Scripts/python.exe tests/run_all_tests.py
```

Los artefactos se generan en `logs/`.

## Archivos clave (resumen)

- `anonymization/detector.py` — heurísticas y scoring.
- `anonymization/column_scanner.py` — muestreo y probabilidades por columna.
- `anonymization/scanner.py` — ensamblador de `scan_summary` y `decision_table`.
- `anonymization/anonymizer.py` — pseudonimización determinística y preservación de formato.
- `tests/run_all_tests.py` — ejecutor central y generador de `logs/ejecucion_<timestamp>.log`.
- `tests/test_scanner_identification.py` — prueba que produce `scan_summary` JSONs.

## Siguientes pasos sugeridos

- Añadir `ARCHITECTURE.drawio` o PlantUML si deseas un diagrama visual.
- Documentar formatos de `scan_summary` JSON y esquema del `decision_table` si necesitas interoperabilidad.

---
Archivo generado automáticamente: `ARCHITECTURE.md`.
