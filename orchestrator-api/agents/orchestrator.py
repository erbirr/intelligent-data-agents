# agents/orchestrator.py - Orquestador inteligente del Universo MCP.
import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from llm.pattern_analyzer import PatternAnalyzer
from mcp.base import MCPAgent, MCPMessage, MCPMessageType

logger = logging.getLogger(__name__)

class OrchestratorAgent(MCPAgent):
    """
    Orquestador inteligente que coordina agentes MCP usando IA.
    
    El orquestador es el 'cerebro' del sistema que:
    1. Analiza consultas en lenguaje natural usando Gemini LLM
    2. Decide inteligentemente qué agentes involucrar y en qué orden
    3. Coordina la comunicación entre agentes especializados
    4. Combina y sintetiza resultados de múltiples fuentes
    5. Optimiza el flujo de trabajo según el contexto
    
    Tipos de consultas soportadas:
    - Consultas simples: Dirigidas a un agente especializado
    - Consultas híbridas: Combinan datos de grafo y relacionales
    - Consultas en cadena: El resultado de uno alimenta al siguiente
    - Consultas paralelas: Múltiples agentes ejecutan simultáneamente
    
    Totalmente basado en IA, sin fallbacks de regex.
    """
    
    def __init__(self, neo4j_agent, postgres_agent):
        super().__init__("orchestrator")
        
        # Referencias a los agentes especializados
        self.neo4j_agent = neo4j_agent
        self.postgres_agent = postgres_agent
        
        # Conectar este agente como cliente de los otros servidores
        self.connect_to_server("neo4j", neo4j_agent)
        self.connect_to_server("postgres", postgres_agent)
        
        # Analizador inteligente de patrones usando Gemini LLM
        self.pattern_analyzer = PatternAnalyzer(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        )
        
        # Registro de herramientas del orquestador
        self._register_orchestrator_tools()
    
    async def initialize(self):
        """Inicializa el orquestador y descubre capacidades de otros agentes"""
        try:
            # Descubrir qué pueden hacer los otros agentes
            self.available_capabilities = await self.discover_servers()
            
            # Registrar recursos del orquestador
            self._register_orchestrator_resources()

            await self.pattern_analyzer.initialize()
            
            self.initialized = True
            logger.info("Orquestador inicializado - capacidades descubiertas de todos los agentes")
            
        except Exception as e:
            logger.error(f"Error inicializando orquestador: {e}")
            raise
    
    def _register_orchestrator_resources(self):
        """Registra recursos que el orquestador puede proveer"""
        
        # Recurso: mapa completo del sistema
        self.register_resource("system_map", self._get_system_map)
        
        # Recurso: capacidades disponibles
        self.register_resource("available_capabilities", self._get_available_capabilities)
        
        # Recurso: estadísticas combinadas
        self.register_resource("combined_statistics", self._get_combined_statistics)
        
        # Recurso: esquema unificado
        self.register_resource("unified_schema", self._get_unified_schema)
    
    def _register_orchestrator_tools(self):
        """Registra herramientas específicas del orquestador"""
        
        # Herramienta: consulta inteligente
        self.register_tool(
            "smart_query",
            self._smart_query,
            "Analiza una consulta en lenguaje natural y la ejecuta usando los agentes apropiados"
        )
        
        # Herramienta: consulta híbrida
        self.register_tool(
            "hybrid_query",
            self._hybrid_query,
            "Ejecuta consultas que requieren datos tanto de grafos como relacionales"
        )
        
        # Herramienta: sincronización de datos
        self.register_tool(
            "sync_data",
            self._sync_data,
            "Sincroniza datos entre Neo4j y PostgreSQL"
        )
        
        # Herramienta: análisis comparativo
        self.register_tool(
            "comparative_analysis",
            self._comparative_analysis,
            "Realiza análisis comparativo usando ambas fuentes de datos"
        )
        
        # Herramienta: flujo de trabajo personalizado
        self.register_tool(
            "custom_workflow",
            self._custom_workflow,
            "Ejecuta un flujo de trabajo personalizado con múltiples pasos"
        )
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Función principal para procesar consultas.
        Esta es la entrada principal que usa el endpoint de FastAPI.
        """
        if context is None:
            context = {}
        
        logger.info(f"Orquestador procesando: {query}")
        
        try:
            # Analizar el tipo de consulta
            query_analysis = await self._analyze_query(query)
            
            # Determinar estrategia de ejecución
            execution_strategy = self._determine_execution_strategy(query_analysis)
            
            # Ejecutar según la estrategia
            result = await self._execute_strategy(query, query_analysis, execution_strategy, context)
            
            return {
                "data": result,
                "metadata": {
                    "query": query,
                    "analysis": query_analysis,
                    "strategy": execution_strategy,
                    "agents_used": result.get("agents_used", []),
                    "execution_time": result.get("execution_time", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error procesando consulta: {e}")
            return {
                "data": {"error": str(e)},
                "metadata": {
                    "query": query,
                    "error": True,
                    "error_message": str(e)
                }
            }
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analiza una consulta usando IA para determinar qué agentes necesita.
        
        Utiliza exclusivamente Gemini LLM para análisis inteligente de consultas
        en lenguaje natural. No hay fallbacks basados en regex.
        """
        try:
            logger.debug(f"Analizando consulta con IA: '{query[:50]}...'")
            
            # Obtener análisis inteligente del LLM
            llm_analysis = await self.pattern_analyzer.analyze_query(query)
            
            # Adaptar el formato del LLM al formato esperado por el orquestador
            analysis = {
                "original_query": query,
                "needs_graph": llm_analysis["needs_graph"],
                "needs_relational": llm_analysis["needs_relational"],
                "needs_both": llm_analysis["needs_both"],
                "complexity": llm_analysis["complexity"],
                "identified_patterns": llm_analysis["identified_patterns"],
                "suggested_agents": llm_analysis["suggested_agents"],
                "analysis_method": llm_analysis["analysis_method"],
                "confidence": llm_analysis.get("confidence", 0)
            }
            
            # Incluir razonamiento del LLM si está disponible
            if "llm_reasoning" in llm_analysis:
                analysis["llm_reasoning"] = llm_analysis["llm_reasoning"]
            
            logger.info(f"✅ Análisis IA exitoso: {analysis['complexity']} - "
                       f"Agentes: {analysis['suggested_agents']} - "
                       f"Confianza: {analysis['confidence']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis IA: {e}")
            # En caso de error completo, usar configuración conservadora
            return {
                "original_query": query,
                "needs_graph": False,
                "needs_relational": True,  # Default a PostgreSQL como más seguro
                "needs_both": False,
                "complexity": "simple",
                "identified_patterns": [],
                "suggested_agents": ["postgres"],
                "analysis_method": "emergency_default",
                "confidence": 0.5,
                "error": str(e)
            }
    
    
    def _determine_execution_strategy(self, query_analysis: Dict[str, Any]) -> str:
        """
        Determina la estrategia de ejecución basada en el análisis de la consulta.
        
        Estrategias disponibles:
        - single_agent: Usar un solo agente
        - parallel: Consultar múltiples agentes en paralelo
        - sequential: Consultar agentes en secuencia (el resultado de uno alimenta al otro)
        - hybrid: Combinar resultados de múltiples agentes
        """
        
        if query_analysis["needs_both"]:
            if query_analysis["complexity"] == "hybrid":
                return "sequential"  # Uno alimenta al otro
            else:
                return "parallel"   # Consultar ambos y combinar
        elif len(query_analysis["suggested_agents"]) == 1:
            return "single_agent"
        else:
            return "parallel"
    
    async def _execute_strategy(self, query: str, analysis: Dict[str, Any], 
                             strategy: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la consulta según la estrategia determinada"""
        
        start_time = asyncio.get_event_loop().time()
        
        if strategy == "single_agent":
            result = await self._execute_single_agent(query, analysis, context)
        elif strategy == "parallel":
            result = await self._execute_parallel(query, analysis, context)
        elif strategy == "sequential":
            result = await self._execute_sequential(query, analysis, context)
        elif strategy == "hybrid":
            result = await self._execute_hybrid(query, analysis, context)
        else:
            raise ValueError(f"Estrategia desconocida: {strategy}")
        
        end_time = asyncio.get_event_loop().time()
        result["execution_time"] = round(end_time - start_time, 3)
        
        return result
    
    async def _execute_single_agent(self, query: str, analysis: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta consulta usando un solo agente"""
        
        agent_name = analysis["suggested_agents"][0]
        
        if agent_name == "neo4j":
            # Convertir consulta natural a operación Neo4j
            result = await self._query_neo4j_natural(query, context)
        else:
            # Convertir consulta natural a operación PostgreSQL
            result = await self._query_postgres_natural(query, context)
        
        return {
            "results": result,
            "agents_used": [agent_name],
            "strategy": "single_agent"
        }
    
    async def _execute_parallel(self, query: str, analysis: Dict[str, Any], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta consultas en paralelo en múltiples agentes"""
        
        tasks = []
        agents_used = []
        
        if "neo4j" in analysis["suggested_agents"]:
            tasks.append(self._query_neo4j_natural(query, context))
            agents_used.append("neo4j")
        
        if "postgres" in analysis["suggested_agents"]:
            tasks.append(self._query_postgres_natural(query, context))
            agents_used.append("postgres")
        
        # Ejecutar en paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        combined_results = {}
        for i, result in enumerate(results):
            agent_name = agents_used[i]
            if isinstance(result, Exception):
                combined_results[agent_name] = {"error": str(result)}
            else:
                combined_results[agent_name] = result
        
        return {
            "results": combined_results,
            "agents_used": agents_used,
            "strategy": "parallel"
        }
    
    async def _execute_sequential(self, query: str, analysis: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta consultas en secuencia, donde el resultado de una alimenta la siguiente"""
        
        # Para consultas secuenciales, usualmente comenzamos con datos relacionales
        # y luego los usamos para crear/consultar el grafo, o viceversa
        
        agents_used = []
        step_results = []
        
        if "postgres" in analysis["suggested_agents"] and "neo4j" in analysis["suggested_agents"]:
            # Paso 1: Obtener datos de PostgreSQL
            postgres_result = await self._query_postgres_natural(query, context)
            agents_used.append("postgres")
            step_results.append({"agent": "postgres", "result": postgres_result})
            
            # Paso 2: Usar esos datos para enriquecer con Neo4j
            enhanced_context = {**context, "postgres_data": postgres_result}
            neo4j_result = await self._query_neo4j_natural(query, enhanced_context)
            agents_used.append("neo4j")
            step_results.append({"agent": "neo4j", "result": neo4j_result})
        
        return {
            "results": step_results,
            "agents_used": agents_used,
            "strategy": "sequential"
        }
    
    async def _execute_hybrid(self, query: str, analysis: Dict[str, Any], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta consulta híbrida combinando inteligentemente los resultados"""
        
        # Primero ejecutar en paralelo
        parallel_result = await self._execute_parallel(query, analysis, context)
        
        # Luego combinar los resultados de manera inteligente
        combined_data = await self._intelligent_merge(
            parallel_result["results"], 
            query, 
            context
        )
        
        return {
            "results": combined_data,
            "agents_used": parallel_result["agents_used"],
            "strategy": "hybrid"
        }
    
    async def _query_neo4j_natural(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte consulta natural en operaciones Neo4j apropiadas"""
        
        # Esta función 'traduce' lenguaje natural a operaciones específicas de Neo4j
        # En una implementación más avanzada, aquí podríamos usar NLP o AI
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["esquema", "estructura", "labels"]):
            return await self.request_resource("neo4j", "graph_schema")
        elif any(word in query_lower for word in ["estadísticas", "stats", "resumen"]):
            return await self.request_resource("neo4j", "graph_stats")
        elif any(word in query_lower for word in ["nodos", "nodes"]):
            return await self.request_resource("neo4j", "nodes_by_label")
        elif any(word in query_lower for word in ["relaciones", "relationships"]):
            return await self.request_resource("neo4j", "relationships_by_type")
        else:
            # Consulta genérica - obtener estadísticas generales
            return await self.request_resource("neo4j", "graph_stats")
    
    async def _query_postgres_natural(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte consulta natural en operaciones PostgreSQL apropiadas"""
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["esquema", "estructura", "tablas"]):
            return await self.request_resource("postgres", "database_schema")
        elif any(word in query_lower for word in ["estadísticas", "stats", "resumen"]):
            return await self.request_resource("postgres", "table_statistics")
        elif any(word in query_lower for word in ["columnas", "columns"]):
            return await self.request_resource("postgres", "columns_info")
        elif any(word in query_lower for word in ["relaciones", "foreign keys"]):
            return await self.request_resource("postgres", "table_relationships")
        else:
            # Consulta genérica - obtener esquema general
            return await self.request_resource("postgres", "database_schema")
    
    async def _intelligent_merge(self, results: Dict[str, Any], query: str, 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Combina inteligentemente resultados de múltiples agentes"""
        
        merged = {
            "summary": "Datos combinados de múltiples fuentes",
            "sources": list(results.keys()),
            "data": results,
            "insights": []
        }
        
        # Generar insights básicos
        if "neo4j" in results and "postgres" in results:
            neo4j_data = results["neo4j"]
            postgres_data = results["postgres"]
            
            # Comparar complejidad de datos
            if isinstance(neo4j_data, dict) and "total_nodes" in neo4j_data:
                if isinstance(postgres_data, dict) and "total_tables" in postgres_data:
                    merged["insights"].append(
                        f"Sistema híbrido: {neo4j_data['total_nodes']} nodos en grafo, "
                        f"{postgres_data['total_tables']} tablas relacionales"
                    )
        
        return merged
    
    # ===== FUNCIONES DE RECURSOS DEL ORQUESTADOR =====
    
    async def _get_system_map(self) -> Dict[str, Any]:
        """Proporciona un mapa completo del sistema"""
        return {
            "orchestrator": {
                "name": self.name,
                "capabilities": list(self.tools.keys()),
                "connected_agents": list(self.connected_servers.keys())
            },
            "available_capabilities": self.available_capabilities,
            "system_status": "operational"
        }
    
    async def _get_available_capabilities(self) -> Dict[str, Any]:
        """Retorna todas las capacidades disponibles en el sistema"""
        return self.available_capabilities
    
    async def _get_combined_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas combinadas de todos los agentes"""
        
        stats = {"timestamp": asyncio.get_event_loop().time()}
        
        try:
            # Obtener stats de Neo4j
            neo4j_stats = await self.request_resource("neo4j", "graph_stats")
            stats["neo4j"] = neo4j_stats
        except Exception as e:
            stats["neo4j"] = {"error": str(e)}
        
        try:
            # Obtener stats de PostgreSQL
            postgres_stats = await self.request_resource("postgres", "table_statistics")
            stats["postgres"] = postgres_stats
        except Exception as e:
            stats["postgres"] = {"error": str(e)}
        
        return stats
    
    async def _get_unified_schema(self) -> Dict[str, Any]:
        """Crea un esquema unificado combinando ambas fuentes"""
        
        unified = {
            "graph_schema": None,
            "relational_schema": None,
            "integration_points": []
        }
        
        try:
            unified["graph_schema"] = await self.request_resource("neo4j", "graph_schema")
        except Exception as e:
            unified["graph_schema"] = {"error": str(e)}
        
        try:
            unified["relational_schema"] = await self.request_resource("postgres", "database_schema")
        except Exception as e:
            unified["relational_schema"] = {"error": str(e)}
        
        # Identificar posibles puntos de integración
        # (Esta lógica podría ser más sofisticada en una implementación real)
        unified["integration_points"] = [
            "Tablas de PostgreSQL pueden convertirse en nodos de Neo4j",
            "Foreign keys de PostgreSQL pueden convertirse en relaciones de Neo4j",
            "Resultados de consultas de grafos pueden enriquecer análisis SQL"
        ]
        
        return unified
    
    # ===== HERRAMIENTAS ESPECÍFICAS DEL ORQUESTADOR =====
    
    async def _smart_query(self, natural_query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Implementa la consulta inteligente - la función principal del orquestador"""
        return await self.process_query(natural_query, context)
    
    async def _hybrid_query(self, graph_query: str, sql_query: str, 
                          merge_strategy: str = "combine") -> Dict[str, Any]:
        """Ejecuta consultas específicas en ambos agentes y las combina"""
        
        # Ejecutar consultas en paralelo
        neo4j_task = self.execute_tool("neo4j", "execute_cypher", {"query": graph_query})
        postgres_task = self.execute_tool("postgres", "execute_sql", {"query": sql_query})
        
        neo4j_result, postgres_result = await asyncio.gather(neo4j_task, postgres_task)
        
        if merge_strategy == "combine":
            return {
                "neo4j_results": neo4j_result,
                "postgres_results": postgres_result,
                "merge_strategy": merge_strategy
            }
        else:
            # Otras estrategias de merge podrían implementarse aquí
            return await self._intelligent_merge(
                {"neo4j": neo4j_result, "postgres": postgres_result},
                f"Hybrid: {graph_query} + {sql_query}",
                {}
            )
    
    async def _sync_data(self, source_agent: str, target_agent: str, 
                       sync_config: Dict[str, Any]) -> Dict[str, Any]:
        """Sincroniza datos entre agentes"""
        
        # Esta es una funcionalidad avanzada para sincronizar datos
        # Por ejemplo, exportar tabla de PostgreSQL como nodos en Neo4j
        
        if source_agent == "postgres" and target_agent == "neo4j":
            # Exportar datos relacionales como grafo
            export_result = await self.execute_tool("postgres", "export_for_graph", sync_config)
            
            # Crear nodos en Neo4j con los datos exportados
            created_nodes = []
            for node_data in export_result["nodes"]:
                node_result = await self.execute_tool("neo4j", "create_node", {
                    "label": node_data["label"],
                    "properties": node_data["properties"]
                })
                created_nodes.append(node_result)
            
            return {
                "sync_direction": "postgres_to_neo4j",
                "exported_nodes": len(export_result["nodes"]),
                "created_nodes": len(created_nodes),
                "success": True
            }
        
        else:
            raise ValueError(f"Sincronización {source_agent} -> {target_agent} no implementada")
    
    async def _comparative_analysis(self, analysis_type: str, 
                                  parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza análisis comparativo usando ambas fuentes de datos"""
        
        if analysis_type == "data_distribution":
            # Comparar distribución de datos entre ambas fuentes
            neo4j_stats = await self.request_resource("neo4j", "graph_stats")
            postgres_stats = await self.request_resource("postgres", "table_statistics")
            
            return {
                "analysis_type": analysis_type,
                "neo4j_data_points": neo4j_stats.get("total_nodes", 0),
                "postgres_data_points": sum([stat.get("live_tuples", 0) 
                                           for stat in postgres_stats.get("table_statistics", [])]),
                "comparison": "Análisis de distribución de datos completado"
            }
        
        else:
            raise ValueError(f"Tipo de análisis {analysis_type} no soportado")
    
    async def _custom_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ejecuta un flujo de trabajo personalizado con múltiples pasos"""
        
        results = []
        
        for i, step in enumerate(workflow_steps):
            try:
                agent = step["agent"]
                tool = step["tool"]
                params = step.get("params", {})
                
                # Ejecutar paso
                step_result = await self.execute_tool(agent, tool, params)
                
                results.append({
                    "step": i + 1,
                    "agent": agent,
                    "tool": tool,
                    "result": step_result,
                    "success": True
                })
                
                # El resultado de este paso puede alimentar al siguiente
                # (implementar lógica más sofisticada según necesidades)
                
            except Exception as e:
                results.append({
                    "step": i + 1,
                    "agent": step.get("agent", "unknown"),
                    "tool": step.get("tool", "unknown"),
                    "error": str(e),
                    "success": False
                })
                # Decidir si continuar o parar en caso de error
                break
        
        return {
            "workflow_steps": len(workflow_steps),
            "completed_steps": len(results),
            "results": results,
            "success": all(r.get("success", False) for r in results)
        }
    
    async def handle_request(self, message: MCPMessage) -> MCPMessage:
        """Maneja peticiones MCP dirigidas al orquestador"""
        
        # El orquestador puede manejar peticiones como cualquier otro agente MCP
        # pero también tiene lógica especial para coordinar otros agentes
        
        try:
            if message.method == "get_resource":
                resource_name = message.params.get("resource_name")
                if resource_name in self.resources:
                    resource_func = self.resources[resource_name]
                    result = await resource_func()
                    
                    return MCPMessage(
                        id=message.id,
                        type=MCPMessageType.RESPONSE,
                        method=message.method,
                        result=result
                    )
                else:
                    return MCPMessage(
                        id=message.id,
                        type=MCPMessageType.RESPONSE,
                        method=message.method,
                        error=f"Recurso '{resource_name}' no encontrado en orquestador"
                    )
            
            elif message.method == "execute_tool":
                tool_name = message.params.get("tool_name")
                tool_params = message.params.get("tool_params", {})
                
                if tool_name in self.tools:
                    tool_func = self.tools[tool_name]["function"]
                    result = await tool_func(**tool_params)
                    
                    return MCPMessage(
                        id=message.id,
                        type=MCPMessageType.RESPONSE,
                        method=message.method,
                        result=result
                    )
                else:
                    return MCPMessage(
                        id=message.id,
                        type=MCPMessageType.RESPONSE,
                        method=message.method,
                        error=f"Herramienta '{tool_name}' no encontrada en orquestador"
                    )
            
            else:
                return MCPMessage(
                    id=message.id,
                    type=MCPMessageType.RESPONSE,
                    method=message.method,
                    error=f"Método '{message.method}' no soportado por orquestador"
                )
        
        except Exception as e:
            logger.error(f"Error en orquestador manejando petición: {e}")
            return MCPMessage(
                id=message.id,
                type=MCPMessageType.RESPONSE,
                method=message.method,
                error=str(e)
            )
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna el estado actual del orquestador con verificación de agentes"""
        base_status = await super().get_status()
        
        # Verificar estado de agentes conectados
        connected = True
        agent_statuses = {}
        connection_details = {}
        
        try:
            # Verificar Neo4j agent
            if self.neo4j_agent:
                neo4j_status = await self.neo4j_agent.get_status()
                agent_statuses["neo4j"] = neo4j_status
                if not neo4j_status.get("connected", False):
                    connected = False
            else:
                agent_statuses["neo4j"] = {"connected": False, "error": "No inicializado"}
                connected = False
            
            # Verificar PostgreSQL agent
            if self.postgres_agent:
                postgres_status = await self.postgres_agent.get_status()
                agent_statuses["postgres"] = postgres_status
                if not postgres_status.get("connected", False):
                    connected = False
            else:
                agent_statuses["postgres"] = {"connected": False, "error": "No inicializado"}
                connected = False
            
            # Verificar Pattern Analyzer / LLM
            llm_status = {"connected": False}
            if hasattr(self, 'pattern_analyzer') and self.pattern_analyzer:
                try:
                    llm_stats = await self.get_llm_stats()
                    llm_status = {"connected": True, "stats": llm_stats}
                except Exception as e:
                    llm_status = {"connected": False, "error": str(e)}
            
            connection_details = {
                "neo4j_connected": agent_statuses["neo4j"].get("connected", False),
                "postgres_connected": agent_statuses["postgres"].get("connected", False),
                "llm_connected": llm_status["connected"],
                "all_systems_operational": connected and llm_status["connected"]
            }
            
        except Exception as e:
            connected = False
            connection_details = {"error": str(e)}
        
        # Agregar información específica del orquestador
        base_status.update({
            "connected": connected,
            "connection_details": connection_details,
            "agent_type": "orchestrator",
            "agent_statuses": agent_statuses,
            "llm_status": llm_status
        })
        
        return base_status
    
    async def close(self):
        """Cierra el orquestador y el analizador de patrones"""
        # 🔴 NUEVO: Cerrar también el pattern_analyzer
        if hasattr(self, 'pattern_analyzer'):
            await self.pattern_analyzer.close()
        
        logger.info("Orquestador cerrado")

    # 🔴 NUEVO: Método para obtener estadísticas del analizador LLM
    async def get_llm_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del uso del LLM"""
        if hasattr(self, 'pattern_analyzer'):
            return await self.pattern_analyzer.get_stats()
        return {"error": "Pattern analyzer not available"}