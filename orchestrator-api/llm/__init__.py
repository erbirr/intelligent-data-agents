# llm/__init__.py
"""
Módulo LLM para integración con Vertex AI Gemini 2.0 Flash.

Este módulo encapsula toda la lógica de procesamiento de lenguaje natural
de forma completamente independiente, permitiendo que tu Universo MCP existente
evolucione de patrones regex a comprensión semántica real sin romper nada.

Filosofía del diseño:
- Autocontenido: Todo lo relacionado con LLM está aquí
- Intercambiable: Puede activarse/desactivarse sin afectar el sistema
- Robusto: Siempre tiene fallback a patrones tradicionales
"""

from .gemini_client import GeminiClient
from .pattern_analyzer import PatternAnalyzer

# Definir qué clases están disponibles públicamente
__all__ = ['GeminiClient', 'PatternAnalyzer']

# Información del módulo para debugging y monitoreo
__version__ = '1.0.0'
__author__ = 'MCP Microservice Tecnoandina'
__description__ = 'Vertex AI Gemini 2.0 Flash integration for intelligent query analysis'

# Configuraciones por defecto que pueden ser sobrescritas
DEFAULT_CONFIG = {
    'model_name': 'gemini-2.0-flash-001',
    'location': 'us-central1',
    'max_retries': 3,
    'timeout': 30,
    'cache_size': 100
}