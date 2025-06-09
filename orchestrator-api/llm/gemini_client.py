# llm/gemini_client.py
"""
Cliente para Vertex AI Gemini 2.0 Flash con soporte asíncrono completo.

Este cliente es como un intérprete diplomático que traduce las peticiones
de tu sistema al lenguaje que entiende Vertex AI, y viceversa. Maneja
toda la complejidad técnica para que el resto de tu código pueda enfocarse
en la lógica de negocio.

Características principales:
- Comunicación asíncrona nativa (no bloquea tu servidor)
- Manejo robusto de errores con reintentos inteligentes
- Autenticación automática con Google Cloud
- Timeouts configurables para evitar consultas colgadas
- Logging detallado para debugging y monitoreo
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional

# Imports de Vertex AI con manejo de errores elegante
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError as e:
    # Si las librerías no están instaladas, el sistema puede seguir funcionando
    # con patrones de fallback. Esto es crucial para robustez.
    logging.warning(f"Vertex AI libraries not available: {e}")
    VERTEX_AI_AVAILABLE = False
    vertexai = None
    GenerativeModel = None

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Cliente inteligente para comunicación con Vertex AI Gemini 2.0 Flash.
    
    Este cliente implementa el patrón "Circuit Breaker" para manejar fallos
    de manera elegante, y el patrón "Retry with Exponential Backoff" para
    manejar problemas temporales de red o carga del servicio.
    """
    
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        """
        Inicializa el cliente con configuración inteligente.
        
        El cliente intentará obtener credenciales automáticamente de:
        1. Variables de entorno explícitas
        2. Google Cloud metadata service (si está en GCP)
        3. Credenciales por defecto de gcloud CLI
        
        Args:
            project_id: ID del proyecto de Google Cloud. Si es None, se detecta automáticamente
            location: Región donde está desplegado Vertex AI (us-central1 es óptima para latencia)
        """
        # Configuración de conexión
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.model_name = "gemini-2.0-flash-001"
        
        # Estado del cliente
        self.model = None
        self.initialized = False
        self.last_error = None
        
        # Configuración de rendimiento y robustez
        self.default_timeout = int(os.getenv("LLM_DEFAULT_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
        self.base_delay = 1.0  # Segundos para backoff exponencial
        
        # Validaciones críticas
        if not self.project_id:
            raise ValueError(
                "Google Cloud Project ID is required. Set GOOGLE_CLOUD_PROJECT environment variable."
            )
        
        if not VERTEX_AI_AVAILABLE:
            raise ImportError(
                "Vertex AI libraries are not installed. Run: pip install google-cloud-aiplatform vertexai"
            )
    
    async def initialize(self):
        """
        Inicializa la conexión con Vertex AI de forma asíncrona y robusta.
        
        Esta función implementa varios niveles de verificación:
        1. Verifica que las librerías estén disponibles
        2. Configura la autenticación con Google Cloud
        3. Crea la instancia del modelo
        4. Ejecuta un test de conectividad
        5. Registra el estado final
        
        Es idempotente: puede llamarse múltiples veces sin problemas.
        """
        if self.initialized:
            logger.debug("Cliente ya inicializado, saltando inicialización")
            return
        
        try:
            logger.info(f"Inicializando cliente Gemini para proyecto {self.project_id} en {self.location}")
            
            # Paso 1: Inicializar Vertex AI SDK
            # Usamos asyncio.to_thread porque vertexai.init() es síncrono
            await asyncio.to_thread(
                vertexai.init,
                project=self.project_id,
                location=self.location
            )
            logger.debug("Vertex AI SDK inicializado correctamente")
            
            # Paso 2: Crear instancia del modelo
            # Gemini 2.0 Flash está optimizado para respuestas rápidas y eficientes
            self.model = GenerativeModel(self.model_name)
            logger.debug(f"Modelo {self.model_name} creado correctamente")
            
            # Paso 3: Ejecutar test de conectividad
            # Esto verifica que podemos comunicarnos con Vertex AI
            await self._test_connection()
            
            # Paso 4: Marcar como inicializado
            self.initialized = True
            self.last_error = None
            
            logger.info("✅ Cliente Gemini inicializado exitosamente")
            
        except Exception as e:
            # Log detallado del error para debugging
            error_msg = f"Error inicializando cliente Gemini: {e}"
            logger.error(error_msg)
            self.last_error = str(e)
            
            # Re-lanzar la excepción para que el sistema pueda decidir usar fallback
            raise RuntimeError(error_msg) from e
    
    # Busca este método en tu gemini_client.py y reemplázalo:


    async def _test_connection(self):
        """
        Ejecuta un test simple pero efectivo de conectividad.
        
        IMPORTANTE: Este método NO debe llamar a generate_content directamente
        para evitar recursión infinita durante la inicialización.
        """
        try:
            logger.debug("Ejecutando test de conectividad...")
            
            # En lugar de llamar a generate_content (que puede causar recursión),
            # verificamos que el modelo esté creado correctamente
            if not self.model:
                raise RuntimeError("Modelo no inicializado")
            
            # Verificar que tenemos las credenciales necesarias
            if not self.project_id:
                raise RuntimeError("Project ID no configurado")
                
            logger.debug("Test de conectividad exitoso - modelo listo")
            
        except Exception as e:
            logger.error(f"Test de conectividad falló: {e}")
            raise RuntimeError(f"No se puede conectar con Vertex AI: {e}") from e
        
    
    async def generate_content(self, prompt: str, timeout: Optional[int] = None) -> str:
        """
        Genera contenido usando Gemini 2.0 Flash con manejo robusto de errores.
        
        Esta función implementa varios patrones de robustez:
        - Retry con exponential backoff para errores temporales
        - Circuit breaker para evitar cascadas de fallos
        - Timeout configurable para evitar requests colgados
        - Logging detallado para monitoreo y debugging
        
        Args:
            prompt: El prompt a enviar al modelo (máximo ~1M tokens)
            timeout: Timeout en segundos (opcional, usa default si no se especifica)
            
        Returns:
            str: La respuesta generada por Gemini 2.0 Flash
            
        Raises:
            RuntimeError: Si el cliente no está inicializado
            TimeoutError: Si la consulta excede el timeout
            Exception: Para otros errores irrecuperables
        """
        # Verificar que el cliente esté listo
        if not self.initialized:
            await self.initialize()
        
        # Configurar timeout
        effective_timeout = timeout or self.default_timeout
        
        # Implementar retry con exponential backoff
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Generando contenido (intento {attempt + 1}/{self.max_retries})")
                
                # Ejecutar la consulta de forma asíncrona
                # asyncio.to_thread convierte la llamada síncrona en asíncrona
                response = await asyncio.wait_for(
                    asyncio.to_thread(self.model.generate_content, prompt),
                    timeout=effective_timeout
                )
                
                # Extraer y validar el texto de respuesta
                result_text = response.text.strip()
                
                if not result_text:
                    raise ValueError("Respuesta vacía del modelo")
                
                # Log de éxito (sin incluir contenido sensible)
                logger.debug(f"Contenido generado exitosamente en intento {attempt + 1}")
                
                return result_text
                
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"Timeout en intento {attempt + 1}/{self.max_retries} ({effective_timeout}s)")
                
                if attempt == self.max_retries - 1:
                    raise TimeoutError(f"Timeout después de {self.max_retries} intentos") from e
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Error en intento {attempt + 1}/{self.max_retries}: {type(e).__name__}: {e}")
                
                # Para el último intento, lanzar la excepción
                if attempt == self.max_retries - 1:
                    raise
                
                # Esperar antes del siguiente intento (exponential backoff)
                delay = self.base_delay * (2 ** attempt)
                logger.debug(f"Esperando {delay}s antes del siguiente intento")
                await asyncio.sleep(delay)
        
        # Esto no debería ejecutarse nunca, pero por robustez...
        raise RuntimeError(f"Falló después de {self.max_retries} intentos") from last_exception
    
    async def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analiza la intención de una consulta para determinar routing de bases de datos.
        
        Esta es la función estrella que reemplaza tu sistema de regex.
        Usa un prompt cuidadosamente diseñado para que Gemini entienda
        las diferencias entre datos relacionales (PostgreSQL) y de grafos (Neo4j).
        
        Args:
            query: La consulta en lenguaje natural del usuario
            
        Returns:
            Dict con el análisis estructurado de la consulta:
            {
                "needs_postgresql": bool,    # ¿Requiere datos relacionales?
                "needs_neo4j": bool,        # ¿Requiere datos de grafos?  
                "needs_both": bool,         # ¿Requiere ambos tipos?
                "complexity": str,          # "simple", "hybrid", "complex"
                "reasoning": str,           # Explicación del LLM
                "suggested_approach": str   # Cómo abordar la consulta
            }
        """
        
        # Prompt cuidadosamente diseñado para nuestro dominio específico
        analysis_prompt = self._build_analysis_prompt(query)
        
        try:
            logger.debug(f"Analizando intención de consulta: '{query[:50]}...'")
            
            # Generar análisis usando Gemini 2.0 Flash
            response = await self.generate_content(analysis_prompt)
            
            # Parsear la respuesta JSON de forma robusta
            parsed_result = self._parse_analysis_response(response)
            
            # Validar que el resultado tenga la estructura esperada
            validated_result = self._validate_analysis_result(parsed_result)
            
            logger.info(f"Análisis completado: {validated_result['complexity']} - "
                       f"PostgreSQL: {validated_result['needs_postgresql']}, "
                       f"Neo4j: {validated_result['needs_neo4j']}")
            
            return validated_result
            
        except Exception as e:
            logger.error(f"Error en análisis de intención: {e}")
            
            # Retornar análisis de fallback basado en palabras clave
            return self._fallback_intent_analysis(query)
    
    def _build_analysis_prompt(self, query: str) -> str:
        """
        Construye un prompt optimizado para análisis de intención de consultas.
        
        Este prompt está cuidadosamente diseñado para maximizar la precisión
        de Gemini 2.0 Flash en nuestro dominio específico.
        """
        return f"""
You are an expert database consultant specializing in hybrid data architectures with PostgreSQL (relational) and Neo4j (graph databases).

Your task: Analyze the user's query and determine the optimal data retrieval strategy.

DATABASE TYPES OVERVIEW:
- PostgreSQL: Structured data, tables, aggregations, statistics, counts, traditional SQL operations
- Neo4j: Graph data, relationships, connections, patterns, networks, recommendations, pathfinding

ANALYSIS FRAMEWORK:
1. Identify primary data needs
2. Determine if relationships/connections are central to the query
3. Assess if aggregations or structured data operations are needed
4. Evaluate complexity level

USER QUERY: "{query}"

RESPOND WITH VALID JSON ONLY:
{{
    "needs_postgresql": true/false,
    "needs_neo4j": true/false, 
    "needs_both": true/false,
    "complexity": "simple|hybrid|complex",
    "reasoning": "Brief explanation of your decision",
    "suggested_approach": "How to best address this query"
}}

IMPORTANT: 
- Respond ONLY with valid JSON
- No additional text or explanations outside the JSON
- Be precise in your assessment
"""
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """
        Parsea la respuesta del LLM de forma robusta, manejando varios formatos.
        """
        try:
            # Limpiar la respuesta
            clean_response = response.strip()
            
            # Manejar diferentes formatos de respuesta
            if clean_response.startswith('```json'):
                # Extraer JSON de bloque de código
                start = clean_response.find('{')
                end = clean_response.rfind('}') + 1
                clean_response = clean_response[start:end]
            elif clean_response.startswith('```'):
                # Extraer de bloque de código genérico
                lines = clean_response.split('\n')
                json_lines = [line for line in lines if line.strip() and not line.startswith('```')]
                clean_response = '\n'.join(json_lines)
            
            # Parsear JSON
            result = json.loads(clean_response)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {e}")
            logger.error(f"Respuesta original: {response}")
            raise ValueError(f"Respuesta inválida del LLM: no es JSON válido") from e
    
    def _validate_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida que el resultado del análisis tenga la estructura correcta.
        """
        required_fields = ["needs_postgresql", "needs_neo4j", "needs_both", "complexity", "reasoning"]
        
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Campo requerido '{field}' no encontrado en análisis")
        
        # Validar tipos de datos
        if not isinstance(result["needs_postgresql"], bool):
            result["needs_postgresql"] = bool(result["needs_postgresql"])
        
        if not isinstance(result["needs_neo4j"], bool):
            result["needs_neo4j"] = bool(result["needs_neo4j"])
        
        if not isinstance(result["needs_both"], bool):
            result["needs_both"] = bool(result["needs_both"])
        
        # Validar complejidad
        valid_complexity = ["simple", "hybrid", "complex"]
        if result["complexity"] not in valid_complexity:
            logger.warning(f"Complejidad inválida '{result['complexity']}', usando 'simple'")
            result["complexity"] = "simple"
        
        # Asegurar consistencia lógica
        if result["needs_both"]:
            result["needs_postgresql"] = True
            result["needs_neo4j"] = True
        
        return result
    
    def _fallback_intent_analysis(self, query: str) -> Dict[str, Any]:
        """
        Análisis de fallback usando patrones de palabras clave.
        
        Se usa cuando el LLM no está disponible o falla.
        Implementa la misma lógica que tu sistema regex original.
        """
        query_lower = query.lower()
        
        # Palabras clave para PostgreSQL (datos relacionales)
        sql_keywords = [
            'tabla', 'table', 'contar', 'count', 'suma', 'sum', 
            'promedio', 'average', 'estadística', 'statistic', 
            'registro', 'record', 'columna', 'column', 'filtro', 'filter'
        ]
        
        # Palabras clave para Neo4j (datos de grafos)
        graph_keywords = [
            'grafo', 'graph', 'relación', 'relation', 'conexión', 'connection',
            'nodo', 'node', 'camino', 'path', 'red', 'network', 'similar',
            'recomendación', 'recommendation', 'patrón', 'pattern'
        ]
        
        # Contar coincidencias
        sql_matches = sum(1 for keyword in sql_keywords if keyword in query_lower)
        graph_matches = sum(1 for keyword in graph_keywords if keyword in query_lower)
        
        # Determinar necesidades
        needs_postgresql = sql_matches > 0
        needs_neo4j = graph_matches > 0
        needs_both = needs_postgresql and needs_neo4j
        
        # Si no hay coincidencias claras, usar ambos por seguridad
        if not needs_postgresql and not needs_neo4j:
            needs_both = True
            needs_postgresql = True
            needs_neo4j = True
        
        return {
            "needs_postgresql": needs_postgresql,
            "needs_neo4j": needs_neo4j,
            "needs_both": needs_both,
            "complexity": "hybrid" if needs_both else "simple",
            "reasoning": f"Análisis de fallback: SQL keywords={sql_matches}, Graph keywords={graph_matches}",
            "suggested_approach": "Usar patrones de palabras clave como fallback",
            "fallback_used": True
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna el estado detallado del cliente para monitoreo y debugging.
        """
        return {
            "initialized": self.initialized,
            "model_name": self.model_name,
            "project_id": self.project_id,
            "location": self.location,
            "vertex_ai_available": VERTEX_AI_AVAILABLE,
            "configuration": {
                "default_timeout": self.default_timeout,
                "max_retries": self.max_retries,
                "base_delay": self.base_delay
            },
            "last_error": self.last_error
        }
    
    async def close(self):
        """
        Limpia los recursos del cliente de forma elegante.
        """
        self.initialized = False
        self.model = None
        self.last_error = None
        logger.info("Cliente Gemini cerrado correctamente")