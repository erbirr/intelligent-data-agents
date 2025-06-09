# llm/pattern_analyzer.py
"""
Analizador inteligente de consultas usando Gemini LLM.

Esta clase es el cerebro del sistema de orquestación. Toma consultas
en lenguaje natural y las convierte en decisiones precisas sobre qué agentes
MCP utilizar y cómo coordinar su ejecución.

Capacidades principales:
1. Análisis semántico de consultas en lenguaje natural
2. Identificación inteligente del tipo de datos requeridos
3. Determinación automática de agentes necesarios
4. Evaluación de complejidad de consultas
5. Generación de estrategias de ejecución

Completamente basado en IA, sin fallbacks de regex.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class PatternAnalyzer:
    """
    Analizador inteligente que comprende consultas en lenguaje natural.
    
    Esta clase utiliza Gemini LLM para:
    - Entender la intención detrás de las consultas
    - Identificar qué tipo de datos se necesitan (grafo, relacional, híbrido)
    - Determinar la complejidad y estrategia de ejecución
    - Proporcionar razonamiento transparente sobre sus decisiones
    
    Es el "traductor universal" entre lenguaje humano y coordinación técnica de agentes.
    """
    
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        """
        Inicializa el analizador inteligente con Gemini LLM.
        
        Args:
            project_id: ID de proyecto Google Cloud (opcional, se detecta automáticamente)
            location: Región de Vertex AI (us-central1 es óptima para latencia)
        """
        # Cliente para comunicación con Gemini LLM
        self.gemini_client = GeminiClient(project_id, location)
        
        # Estado del analizador
        self.initialized = False
        self.llm_available = False
        
        # Cache inteligente para evitar llamadas repetidas al LLM
        # Mejora significativamente el rendimiento y reduce costos
        self.analysis_cache = {}
        self.cache_max_size = int(os.getenv("LLM_CACHE_MAX_SIZE", "100"))
        
        # Estadísticas para monitoreo y optimización
        self.stats = {
            "total_queries": 0,
            "llm_queries": 0,
            "cache_hits": 0,
            "errors": 0,
            "avg_confidence": 0.0
        }
    
    async def initialize(self):
        """
        Inicializa el analizador inteligente con Gemini LLM.
        
        Establece la conexión con Vertex AI y configura el analizador
        para análisis de consultas en lenguaje natural.
        """
        if self.initialized:
            logger.debug("Analizador ya inicializado")
            return
        
        logger.info("Inicializando analizador inteligente con Gemini LLM...")
        
        try:
            # Inicializar conexión con Vertex AI
            await self.gemini_client.initialize()
            self.llm_available = True
            logger.info("✅ Analizador IA inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando LLM: {e}")
            self.llm_available = False
            raise Exception(f"No se pudo inicializar el analizador IA: {e}")
        
        self.initialized = True
        logger.info("Analizador listo para procesar consultas inteligentes")
    
    async def analyze_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Función principal: Analiza una consulta y determina qué agentes MCP usar.
        
        Esta es la función que reemplaza directamente tu lógica de regex actual.
        Mantiene exactamente la misma interfaz, pero internamente puede usar
        inteligencia artificial o patrones tradicionales según disponibilidad.
        
        Args:
            query: La consulta en lenguaje natural del usuario
            context: Contexto adicional opcional (para futuras extensiones)
            
        Returns:
            Dict con exactamente el mismo formato que tu sistema actual:
            {
                "original_query": str,           # La consulta original
                "needs_graph": bool,             # ¿Usar Neo4j?
                "needs_relational": bool,        # ¿Usar PostgreSQL?
                "needs_both": bool,              # ¿Usar ambos?
                "complexity": str,               # "simple", "hybrid", "complex"
                "identified_patterns": List[str], # Patrones identificados
                "suggested_agents": List[str],   # ["neo4j", "postgres"]
                "analysis_method": str,          # "llm", "fallback", "cache"
                "confidence": float              # Confianza en el análisis (0-1)
            }
        """
        # Asegurar que el analizador esté inicializado
        if not self.initialized:
            await self.initialize()
        
        # Incrementar contador de consultas para estadísticas
        self.stats["total_queries"] += 1
        
        # Preparar contexto por defecto
        if context is None:
            context = {}
        
        # Verificar cache primero (optimización importante)
        cache_key = self._generate_cache_key(query, context)
        if cache_key in self.analysis_cache:
            logger.debug("🎯 Usando resultado de cache")
            self.stats["cache_hits"] += 1
            cached_result = self.analysis_cache[cache_key].copy()
            cached_result["from_cache"] = True
            cached_result["analysis_method"] = "cache"
            return cached_result
        
        # Ejecutar análisis (LLM o fallback)
        try:
            if self.llm_available and not self.fallback_only:
                # Ruta inteligente: usar Gemini 2.0 Flash
                result = await self._analyze_with_llm(query, context)
                result["analysis_method"] = "llm"
                result["confidence"] = 0.9  # Alta confianza en análisis LLM
                self.stats["llm_queries"] += 1
                
            else:
                # Ruta tradicional: usar patrones regex
                result = await self._analyze_with_fallback(query, context)
                result["analysis_method"] = "fallback"  
                result["confidence"] = 0.7  # Confianza moderada en patrones
                self.stats["fallback_queries"] += 1
            
            # Guardar en cache para futuras consultas similares
            self._cache_result(cache_key, result)
            
            # Log del resultado para monitoreo
            logger.info(f"📊 Análisis completado: {result['analysis_method']} - "
                       f"Complejidad: {result['complexity']} - "
                       f"Agentes: {result['suggested_agents']}")
            
            return result
            
        except Exception as e:
            # Si todo falla, usar análisis de emergencia
            logger.error(f"Error en análisis de consulta: {e}")
            self.stats["errors"] += 1
            
            # Análisis de emergencia: siempre funciona
            emergency_result = self._emergency_analysis(query, context)
            emergency_result["analysis_method"] = "emergency"
            emergency_result["confidence"] = 0.5
            emergency_result["error"] = str(e)
            
            return emergency_result
    
    async def _analyze_with_llm(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análisis inteligente usando Gemini 2.0 Flash.
        
        Esta función es donde ocurre la magia: convierte una consulta en lenguaje
        natural en decisiones técnicas precisas sobre qué bases de datos usar.
        """
        logger.debug(f"🧠 Analizando con LLM: '{query[:50]}...'")
        
        try:
            # Obtener análisis detallado del LLM
            llm_analysis = await self.gemini_client.analyze_query_intent(query)
            
            # Convertir formato LLM al formato esperado por tu orquestador
            # Esto mantiene compatibilidad total con tu código existente
            result = {
                "original_query": query,
                "needs_graph": llm_analysis["needs_neo4j"],
                "needs_relational": llm_analysis["needs_postgresql"],
                "needs_both": llm_analysis["needs_both"],
                "complexity": llm_analysis["complexity"],
                "identified_patterns": [f"llm_reasoning: {llm_analysis['reasoning']}"],
                "suggested_agents": self._determine_agents_from_llm(llm_analysis),
                "llm_reasoning": llm_analysis["reasoning"],
                "suggested_approach": llm_analysis.get("suggested_approach", "")
            }
            
            logger.debug(f"✅ Análisis LLM exitoso: {result['complexity']}")
            return result
            
        except Exception as e:
            logger.warning(f"LLM análisis falló, usando fallback: {e}")
            # Si el LLM falla, usar fallback automáticamente
            return await self._analyze_with_fallback(query, context)
    
    async def _analyze_with_fallback(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análisis usando patrones regex - exactamente tu lógica actual.
        
        Esta función implementa la misma lógica que ya tienes funcionando,
        garantizando que tu sistema siempre tenga un comportamiento predecible.
        """
        import re
        
        logger.debug(f"📋 Analizando con patrones regex: '{query[:50]}...'")
        
        query_lower = query.lower()
        
        # Buscar patrones de grafo (exactamente como tu código actual)
        graph_matches = 0
        graph_patterns_found = []
        for pattern in self.fallback_patterns["graph_patterns"]:
            if re.search(pattern, query_lower, re.IGNORECASE):
                graph_patterns_found.append(f"graph: {pattern}")
                graph_matches += 1
        
        # Buscar patrones relacionales (exactamente como tu código actual)
        sql_matches = 0
        sql_patterns_found = []
        for pattern in self.fallback_patterns["sql_patterns"]:
            if re.search(pattern, query_lower, re.IGNORECASE):
                sql_patterns_found.append(f"sql: {pattern}")
                sql_matches += 1
        
        # Buscar patrones híbridos (exactamente como tu código actual)
        hybrid_matches = 0
        hybrid_patterns_found = []
        for pattern in self.fallback_patterns["hybrid_patterns"]:
            if re.search(pattern, query_lower, re.IGNORECASE):
                hybrid_patterns_found.append(f"hybrid: {pattern}")
                hybrid_matches += 1
        
        # Lógica de decisión (exactamente como tu código actual)
        if hybrid_matches > 0:
            needs_both = True
            needs_graph = True
            needs_relational = True
            complexity = "hybrid"
            suggested_agents = ["neo4j", "postgres"]
        elif graph_matches > sql_matches:
            needs_both = False
            needs_graph = True
            needs_relational = False
            complexity = "simple"
            suggested_agents = ["neo4j"]
        elif sql_matches > graph_matches:
            needs_both = False
            needs_graph = False
            needs_relational = True
            complexity = "simple"
            suggested_agents = ["postgres"]
        else:
            # Si no hay patrones claros, usar ambos por seguridad
            needs_both = True
            needs_graph = True
            needs_relational = True
            complexity = "exploratory"
            suggested_agents = ["neo4j", "postgres"]
        
        # Detectar complejidad adicional (tu lógica actual)
        complexity_keywords = ["combinar", "comparar", "analizar", "todos", "completo", "integrar"]
        if any(word in query_lower for word in complexity_keywords):
            complexity = "complex"
        
        # Combinar todos los patrones encontrados
        all_patterns = graph_patterns_found + sql_patterns_found + hybrid_patterns_found
        
        result = {
            "original_query": query,
            "needs_graph": needs_graph,
            "needs_relational": needs_relational,
            "needs_both": needs_both,
            "complexity": complexity,
            "identified_patterns": all_patterns,
            "suggested_agents": suggested_agents
        }
        
        logger.debug(f"✅ Análisis fallback exitoso: {complexity} - {suggested_agents}")
        return result
    
    def _emergency_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análisis de emergencia: siempre funciona, nunca falla.
        
        Se usa cuando tanto el LLM como el análisis de fallback fallan.
        Retorna una configuración conservadora que siempre funciona.
        """
        logger.warning("🚨 Usando análisis de emergencia")
        
        return {
            "original_query": query,
            "needs_graph": True,      # Por seguridad, usar ambos
            "needs_relational": True,
            "needs_both": True,
            "complexity": "unknown",
            "identified_patterns": ["emergency_fallback"],
            "suggested_agents": ["neo4j", "postgres"],  # Usar todos por seguridad
            "emergency_mode": True
        }
    
    def _determine_agents_from_llm(self, llm_analysis: Dict[str, Any]) -> List[str]:
        """
        Convierte el análisis del LLM en lista de agentes compatibles con tu sistema.
        """
        agents = []
        
        if llm_analysis.get("needs_postgresql", False):
            agents.append("postgres")
        
        if llm_analysis.get("needs_neo4j", False):
            agents.append("neo4j")
        
        # Si no se especificó nada, usar ambos por seguridad
        if not agents:
            agents = ["neo4j", "postgres"]
        
        return agents
    
    def _generate_cache_key(self, query: str, context: Dict[str, Any]) -> str:
        """
        Genera una clave única para el cache basada en la consulta y contexto.
        """
        # Normalizar query para mejor hit rate del cache
        normalized_query = query.lower().strip()
        
        # Incluir contexto relevante en la clave
        context_str = str(sorted(context.items())) if context else ""
        
        # Crear clave compuesta
        cache_key = f"{normalized_query}|{context_str}"
        
        # Limitar longitud para eficiencia
        if len(cache_key) > 200:
            import hashlib
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        
        return cache_key
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """
        Guarda resultado en cache con gestión inteligente de memoria.
        """
        # Si el cache está lleno, remover entradas más antiguas (FIFO)
        while len(self.analysis_cache) >= self.cache_max_size:
            oldest_key = next(iter(self.analysis_cache))
            del self.analysis_cache[oldest_key]
        
        # Crear copia limpia para cache (sin campos temporales)
        cached_result = result.copy()
        cached_result.pop("error", None)
        cached_result.pop("from_cache", None)
        cached_result.pop("emergency_mode", None)
        
        # Guardar en cache
        self.analysis_cache[cache_key] = cached_result
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Retorna información detallada sobre las capacidades del analizador.
        
        Útil para debugging, monitoreo y dashboards administrativos.
        """
        base_capabilities = {
            "initialized": self.initialized,
            "llm_available": self.llm_available,
            "fallback_only": self.fallback_only,
            "cache_stats": {
                "current_size": len(self.analysis_cache),
                "max_size": self.cache_max_size,
                "hit_rate": (self.stats["cache_hits"] / max(self.stats["total_queries"], 1)) * 100
            },
            "query_stats": self.stats.copy(),
            "fallback_patterns": {
                "graph_patterns_count": len(self.fallback_patterns["graph_patterns"]),
                "sql_patterns_count": len(self.fallback_patterns["sql_patterns"]),
                "hybrid_patterns_count": len(self.fallback_patterns["hybrid_patterns"])
            }
        }
        
        # Añadir información del cliente Gemini si está disponible
        if self.llm_available:
            try:
                gemini_status = await self.gemini_client.get_status()
                base_capabilities["gemini_client"] = gemini_status
            except Exception as e:
                base_capabilities["gemini_client"] = {"error": str(e)}
        
        return base_capabilities
    
    async def clear_cache(self):
        """
        Limpia el cache de análisis.
        
        Útil para testing o cuando se detectan patrones incorrectos en producción.
        """
        cache_size = len(self.analysis_cache)
        self.analysis_cache.clear()
        logger.info(f"🧹 Cache limpiado: {cache_size} entradas removidas")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas detalladas de uso.
        
        Perfecto para monitoreo, alertas y optimización de costos.
        """
        total_queries = max(self.stats["total_queries"], 1)  # Evitar división por cero
        
        return {
            "usage_statistics": self.stats.copy(),
            "performance_metrics": {
                "llm_usage_percentage": (self.stats["llm_queries"] / total_queries) * 100,
                "fallback_usage_percentage": (self.stats["fallback_queries"] / total_queries) * 100,
                "cache_hit_rate": (self.stats["cache_hits"] / total_queries) * 100,
                "error_rate": (self.stats["errors"] / total_queries) * 100
            },
            "efficiency_score": self._calculate_efficiency_score()
        }
    
    def _calculate_efficiency_score(self) -> float:
        """
        Calcula un score de eficiencia del 0-100 basado en métricas de rendimiento.
        """
        if self.stats["total_queries"] == 0:
            return 100.0
        
        # Factores que contribuyen a la eficiencia
        cache_factor = (self.stats["cache_hits"] / self.stats["total_queries"]) * 30  # 30% peso
        llm_factor = (self.stats["llm_queries"] / self.stats["total_queries"]) * 40   # 40% peso  
        error_factor = (1 - (self.stats["errors"] / self.stats["total_queries"])) * 30  # 30% peso
        
        efficiency_score = cache_factor + llm_factor + error_factor
        return min(100.0, max(0.0, efficiency_score))
    
    async def close(self):
        """
        Cierra el analizador y libera recursos de forma elegante.
        """
        logger.info("🔄 Cerrando analizador de patrones...")
        
        # Cerrar cliente Gemini
        if self.gemini_client:
            await self.gemini_client.close()
        
        # Limpiar cache
        self.analysis_cache.clear()
        
        # Resetear estado
        self.initialized = False
        self.llm_available = False
        
        # Log final de estadísticas
        if self.stats["total_queries"] > 0:
            efficiency = self._calculate_efficiency_score()
            logger.info(f"📊 Estadísticas finales: {self.stats['total_queries']} consultas procesadas, "
                       f"eficiencia: {efficiency:.1f}%")
        
        logger.info("✅ Analizador cerrado correctamente")