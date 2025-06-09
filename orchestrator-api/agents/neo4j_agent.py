# agents/neo4j_agent.py - Agente MCP para Neo4j (CORREGIDO)
import logging
from typing import Any, Dict, List, Optional

from mcp.base import MCPAgent, MCPMessage, MCPMessageType
from neo4j import AsyncGraphDatabase

logger = logging.getLogger(__name__)

class Neo4jAgent(MCPAgent):
    """
    Agente MCP para Neo4j que maneja datos de grafos.
    
    Como servidor MCP: Expone capacidades para consultar y manipular grafos
    Como cliente MCP: Puede solicitar datos de otros agentes para enriquecer el grafo
    """
    
    def __init__(self, uri: str, user: str, password: str, database: str = "multiagentes"):
        super().__init__("neo4j_agent")
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database  # Almacenamos el nombre de la base de datos
        self.driver = None
        
        # Definir las herramientas que este agente puede ejecutar
        self._register_neo4j_tools()

        logger.info(f"Neo4jAgent inicializado - URI: {uri}, Database: {database}")
    
    async def initialize(self):
        """Inicializa la conexión a Neo4j y registra recursos"""
        try:
            # Establecer conexión con Neo4j
            self.driver = AsyncGraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            
            # Verificar conectividad
            await self._verify_connection()

            logger.info(f"Conexión Neo4j establecida - Database: {self.database}")
            
            # Registrar los recursos que este agente puede proveer
            self._register_neo4j_resources()
            
            self.initialized = True
            logger.info("Agente Neo4j inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando agente Neo4j: {e}")
            raise
    
    async def _verify_connection(self):
        """Verifica que la conexión a Neo4j funcione"""
        # CORRECTO: Ya especifica database
        async with self.driver.session(database=self.database) as session:
            result = await session.run("RETURN 1 as test")
            record = await result.single()
            if record["test"] != 1:
                raise Exception("Conexión a Neo4j no funciona correctamente")
    
    def _register_neo4j_resources(self):
        """Registra los recursos que este agente puede proveer"""
        # Recurso: esquema del grafo
        self.register_resource("graph_schema", self._get_graph_schema)
        
        # Recurso: estadísticas del grafo  
        self.register_resource("graph_stats", self._get_graph_statistics)
        
        # Recurso: nodos por etiqueta
        self.register_resource("nodes_by_label", self._get_nodes_by_label)
        
        # Recurso: relaciones por tipo
        self.register_resource("relationships_by_type", self._get_relationships_by_type)
    
    def _register_neo4j_tools(self):
        """Registra las herramientas que este agente puede ejecutar"""
        
        # Herramienta: ejecutar consulta Cypher
        self.register_tool(
            "execute_cypher",
            self._execute_cypher_query,
            "Ejecuta una consulta Cypher personalizada en el grafo"
        )
        
        # Herramienta: buscar nodos
        self.register_tool(
            "find_nodes",
            self._find_nodes,
            "Busca nodos en el grafo por etiqueta y propiedades"
        )
        
        # Herramienta: buscar caminos
        self.register_tool(
            "find_paths",
            self._find_paths,
            "Encuentra caminos entre nodos en el grafo"
        )
        
        # Herramienta: crear nodo
        self.register_tool(
            "create_node",
            self._create_node,
            "Crea un nuevo nodo en el grafo"
        )
        
        # Herramienta: crear relación
        self.register_tool(
            "create_relationship", 
            self._create_relationship,
            "Crea una nueva relación entre nodos"
        )
    
    async def handle_request(self, message: MCPMessage) -> MCPMessage:
        """
        Maneja peticiones MCP dirigidas a este agente.
        Esta es la función central que procesa todas las peticiones.
        """
        try:
            if message.method == "get_resource":
                # Solicitud de un recurso
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
                        error=f"Recurso '{resource_name}' no encontrado"
                    )
            
            elif message.method == "execute_tool":
                # Ejecución de una herramienta
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
                        error=f"Herramienta '{tool_name}' no encontrada"
                    )
            
            else:
                return MCPMessage(
                    id=message.id,
                    type=MCPMessageType.RESPONSE,
                    method=message.method,
                    error=f"Método '{message.method}' no soportado"
                )
        
        except Exception as e:
            logger.error(f"Error manejando petición MCP: {e}")
            return MCPMessage(
                id=message.id,
                type=MCPMessageType.RESPONSE,
                method=message.method,
                error=str(e)
            )
    
    # ===== FUNCIONES DE RECURSOS =====
    
    async def _get_graph_schema(self) -> Dict[str, Any]:
        """Obtiene el esquema completo del grafo"""
        # CORREGIDO: Agregado database=self.database
        async with self.driver.session(database=self.database) as session:
            # Obtener etiquetas de nodos
            labels_result = await session.run("CALL db.labels()")
            labels = [record["label"] async for record in labels_result]
            
            # Obtener tipos de relaciones
            rels_result = await session.run("CALL db.relationshipTypes()")
            relationship_types = [record["relationshipType"] async for record in rels_result]
            
            return {
                "node_labels": labels,
                "relationship_types": relationship_types,
                "total_labels": len(labels),
                "total_relationship_types": len(relationship_types)
            }
    
    async def _get_graph_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del grafo"""
        # CORREGIDO: Agregado database=self.database
        async with self.driver.session(database=self.database) as session:
            # Contar nodos
            nodes_result = await session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = (await nodes_result.single())["node_count"]
            
            # Contar relaciones
            rels_result = await session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_count = (await rels_result.single())["rel_count"]
            
            return {
                "total_nodes": node_count,
                "total_relationships": rel_count,
                "avg_degree": round(rel_count * 2 / node_count if node_count > 0 else 0, 2)
            }
    
    async def _get_nodes_by_label(self) -> Dict[str, int]:
        """Cuenta nodos por cada etiqueta"""
        # CORREGIDO: Agregado database=self.database
        async with self.driver.session(database=self.database) as session:
            query = """
            CALL db.labels() YIELD label
            CALL {
                WITH label
                MATCH (n)
                WHERE label IN labels(n)
                RETURN count(n) as count
            }
            RETURN label, count
            """
            
            results = await session.run(query)
            return {record["label"]: record["count"] async for record in results}
    
    async def _get_relationships_by_type(self) -> Dict[str, int]:
        """Cuenta relaciones por cada tipo"""
        # CORREGIDO: Agregado database=self.database
        async with self.driver.session(database=self.database) as session:
            query = """
            CALL db.relationshipTypes() YIELD relationshipType
            CALL {
                WITH relationshipType
                MATCH ()-[r]->()
                WHERE type(r) = relationshipType
                RETURN count(r) as count
            }
            RETURN relationshipType, count
            """
            
            results = await session.run(query)
            return {record["relationshipType"]: record["count"] async for record in results}
    
    # ===== FUNCIONES DE HERRAMIENTAS =====
    
    async def _execute_cypher_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ejecuta una consulta Cypher personalizada"""
        if parameters is None:
            parameters = {}
            
        # CORREGIDO: Agregado database=self.database
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, parameters)
            records = [record.data() async for record in result]
            
            return {
                "query": query,
                "parameters": parameters,
                "results": records,
                "count": len(records)
            }
    
    async def _find_nodes(self, label: str, properties: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Busca nodos por etiqueta y propiedades opcionales"""
        if properties is None:
            properties = {}
        
        # Construir consulta Cypher dinámicamente
        where_clauses = []
        params = {}
        
        for key, value in properties.items():
            param_name = f"prop_{key}"
            where_clauses.append(f"n.{key} = ${param_name}")
            params[param_name] = value
        
        where_clause = " AND ".join(where_clauses) if where_clauses else ""
        query = f"MATCH (n:{label})"
        if where_clause:
            query += f" WHERE {where_clause}"
        query += " RETURN n LIMIT 100"
        
        # CORREGIDO: Agregado database=self.database
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, params)
            nodes = []
            async for record in result:
                node = record["n"]
                nodes.append({
                    "id": node.element_id,
                    "labels": list(node.labels),
                    "properties": dict(node)
                })
            
            return nodes
    
    async def _find_paths(self, from_node_id: str, to_node_id: str, max_length: int = 5) -> List[Dict[str, Any]]:
        """Encuentra caminos entre dos nodos"""
        query = """
        MATCH path = (start)-[*1..%d]-(end)
        WHERE elementId(start) = $from_id AND elementId(end) = $to_id
        RETURN path
        LIMIT 10
        """ % max_length
        
        # CORREGIDO: Agregado database=self.database
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, {"from_id": from_node_id, "to_id": to_node_id})
            paths = []
            
            async for record in result:
                path = record["path"]
                paths.append({
                    "length": len(path.relationships),
                    "nodes": [{"id": node.element_id, "labels": list(node.labels)} for node in path.nodes],
                    "relationships": [{"type": rel.type, "properties": dict(rel)} for rel in path.relationships]
                })
            
            return paths
    
    async def _create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo nodo en el grafo"""
        # Construir consulta CREATE dinámicamente
        props_str = ", ".join([f"{key}: ${key}" for key in properties.keys()])
        query = f"CREATE (n:{label} {{{props_str}}}) RETURN n"
        
        # CORREGIDO: Agregado database=self.database
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, properties)
            record = await result.single()
            node = record["n"]
            
            return {
                "id": node.element_id,
                "labels": list(node.labels),
                "properties": dict(node),
                "created": True
            }
    
    async def _create_relationship(self, from_node_id: str, to_node_id: str, 
                                 relationship_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crea una nueva relación entre nodos"""
        if properties is None:
            properties = {}
        
        props_str = ", ".join([f"{key}: ${key}" for key in properties.keys()]) if properties else ""
        props_clause = f" {{{props_str}}}" if props_str else ""
        
        query = f"""
        MATCH (a), (b)
        WHERE elementId(a) = $from_id AND elementId(b) = $to_id
        CREATE (a)-[r:{relationship_type}{props_clause}]->(b)
        RETURN r
        """
        
        params = {"from_id": from_node_id, "to_id": to_node_id}
        params.update(properties)
        
        # CORREGIDO: Agregado database=self.database
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, params)
            record = await result.single()
            
            if record:
                rel = record["r"]
                return {
                    "type": rel.type,
                    "properties": dict(rel),
                    "created": True
                }
            else:
                raise Exception("No se pudieron encontrar los nodos especificados")
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna el estado actual del agente con verificación de conexión real"""
        base_status = await super().get_status()
        
        # Verificar conexión real a Neo4j
        connected = False
        connection_details = {}
        
        if self.driver and self.initialized:
            try:
                # Hacer una consulta simple para verificar conectividad
                # YA ESTÁ CORRECTO: usa database=self.database
                async with self.driver.session(database=self.database) as session:
                    result = await session.run("RETURN 1 as test")
                    await result.single()
                    connected = True
                    connection_details = {
                        "uri": self.uri,
                        "user": self.user,
                        "database": self.database,  # Agregado para mejor información
                        "database_available": True
                    }
            except Exception as e:
                connected = False
                connection_details = {
                    "uri": self.uri,
                    "user": self.user,
                    "database": self.database,  # Agregado para mejor información
                    "error": str(e),
                    "database_available": False
                }
        
        # Agregar información específica de Neo4j
        base_status.update({
            "connected": connected,
            "connection_details": connection_details,
            "agent_type": "neo4j",
            "uri": self.uri,
            "database": self.database  # Agregado para claridad
        })
        
        return base_status
    
    async def close(self):
        """Cierra la conexión a Neo4j"""
        if self.driver:
            await self.driver.close()
            logger.info(f"Conexión a Neo4j cerrada (database: {self.database})")