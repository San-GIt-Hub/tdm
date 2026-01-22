"""
Módulo de anonimización y detección de datos sensibles.

Proporciona herramientas para detectar, escanear y anonimizar datos sensibles
como cédulas, RUCs, emails y teléfonos de Ecuador.
"""

# Agregar módulo anonymization al path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar clases principales
from .scanner import DataScanner
from .detector import SensitiveDataDetector
from .anonymizer import DataAnonymizer
from .rules import AnonymizationRule, RuleEngine
from .validators_ec import EcuadorValidators

# Definir qué se exporta cuando se hace "from anonymization import *"
__all__ = [
    'DataScanner',
    'SensitiveDataDetector',
    'DataAnonymizer',
    'AnonymizationRule',
    'RuleEngine',
    'EcuadorValidators'
]
