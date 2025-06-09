# agents/postgres_agent.py - Agente MCP para PostgreSQL
import json
import logging
from typing import Any, Dict, List, Optional, Union

import asyncpg
from mcp.base import MCPAgent, MCPMessage, MCPMessageType

logger = logging.getLogger(__name__)

class PostgresAgent(MCPAgent):
    """
    Agente MCP para PostgreSQL que maneja datos relacionales.
    
    Como servidor MCP: Expone capacidades para consultar y manipular datos relacionales
    Como cliente MCP: Puede solicitar datos de otros agentes para enriquecer la base de datos
    
    La belleza de este agente es que puede trabajar en conjunto con el agente Neo4j:
    - Puede exportar datos relacionales para crear grafos
    - Puede importar resultados de grafos para análisis SQL
    """
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        super().__init__("postgres_agent")
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.pool = None
        
        # Definir las herramientas que este agente puede ejecutar
        self._register_postgres_tools()
    
    async def initialize(self):
        """Inicializa el pool de conexiones a PostgreSQL y registra recursos"""
        try:
            # Crear pool de conexiones para mejor rendimiento
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=2,
                max_size=10
            )
            
            # Verificar conectividad
            await self._verify_connection()
            
            # Registrar los recursos que este agente puede proveer
            await self._register_postgres_resources()
            
            self.initialized = True
            logger.info("Agente PostgreSQL inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando agente PostgreSQL: {e}")
            raise
    
    async def _verify_connection(self):
        """Verifica que la conexión a PostgreSQL funcione"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            if result != 1:
                raise Exception("Conexión a PostgreSQL no funciona correctamente")
    
    async def _register_postgres_resources(self):
        """Registra los recursos que este agente puede proveer"""
        
        # Recurso: esquema de la base de datos
        self.register_resource("database_schema", self._get_database_schema)
        
        # Recurso: estadísticas de tablas
        self.register_resource("table_statistics", self._get_table_statistics)
        
        # Recurso: índices disponibles
        self.register_resource("indexes", self._get_indexes_info)
        
        # Recurso: relaciones entre tablas (foreign keys)
        self.register_resource("table_relationships", self._get_table_relationships)
        
        # Recurso: información de columnas
        self.register_resource("columns_info", self._get_columns_info)
    
    def _register_postgres_tools(self):
        """Registra las herramientas que este agente puede ejecutar"""
        
        # Herramienta: ejecutar consulta SQL
        self.register_tool(
            "execute_sql",
            self._execute_sql_query,
            "Ejecuta una consulta SQL personalizada en la base de datos"
        )
        
        # Herramienta: buscar en tablas
        self.register_tool(
            "search_table",
            self._search_table,
            "Busca registros en una tabla específica con filtros"
        )
        
        # Herramienta: insertar datos
        self.register_tool(
            "insert_data",
            self._insert_data,
            "Inserta nuevos registros en una tabla"
        )
        
        # Herramienta: actualizar datos
        self.register_tool(
            "update_data",
            self._update_data,
            "Actualiza registros existentes en una tabla"
        )
        
        # Herramienta: agregar datos para análisis
        self.register_tool(
            "aggregate_data",
            self._aggregate_data,
            "Realiza agregaciones (COUNT, SUM, AVG, etc.) en los datos"
        )
        
        # Herramienta: exportar datos para grafos
        self.register_tool(
            "export_for_graph",
            self._export_for_graph,
            "Exporta datos en formato adecuado para crear grafos en Neo4j"
        )
        
        # Herramienta: crear tabla dinámica
        self.register_tool(
            "create_dynamic_table",
            self._create_dynamic_table,
            "Crea una tabla nueva con estructura dinámica"
        )
    
    async def handle_request(self, message: MCPMessage) -> MCPMessage:
        """
        Maneja peticiones MCP dirigidas a este agente.
        Similar al agente Neo4j, pero optimizado para operaciones relacionales.
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
            logger.error(f"Error manejando petición MCP en PostgreSQL: {e}")
            return MCPMessage(
                id=message.id,
                type=MCPMessageType.RESPONSE,
                method=message.method,
                error=str(e)
            )
    
    # ===== FUNCIONES DE RECURSOS =====
    
    async def _get_database_schema(self) -> Dict[str, Any]:
        """Obtiene el esquema completo de la base de datos - TODAS las tablas de TODOS los esquemas"""
        async with self.pool.acquire() as conn:
            # Consulta mejorada: obtener tablas de TODOS los esquemas (excepto esquemas del sistema)
            tables_query = """
            SELECT 
                table_schema,
                table_name, 
                table_type,
                CASE 
                    WHEN table_schema = 'public' THEN 1
                    ELSE 2
                END as priority
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY priority, table_schema, table_name
            """
            tables = await conn.fetch(tables_query)
            
            # Consulta para vistas (también de todos los esquemas)
            views_query = """
            SELECT 
                table_schema,
                table_name 
            FROM information_schema.views 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY table_schema, table_name
            """
            views = await conn.fetch(views_query)
            
            # Organizar los resultados por esquema para mayor claridad
            tables_by_schema = {}
            total_tables = 0
            
            for row in tables:
                schema = row["table_schema"]
                if schema not in tables_by_schema:
                    tables_by_schema[schema] = []
                
                tables_by_schema[schema].append({
                    "name": row["table_name"],
                    "type": row["table_type"]
                })
                total_tables += 1
            
            views_by_schema = {}
            total_views = 0
            
            for row in views:
                schema = row["table_schema"]
                if schema not in views_by_schema:
                    views_by_schema[schema] = []
                
                views_by_schema[schema].append(row["table_name"])
                total_views += 1

            logger.info(f"Conectando a: host={self.host}, port={self.port}, database={self.database}")
            logger.info(f"Ejecutando consulta: {tables_query}")
            
            return {
                "database_name": self.database,
                "tables_by_schema": tables_by_schema,
                "views_by_schema": views_by_schema,
                "total_tables": total_tables,
                "total_views": total_views,
                "schemas_found": list(tables_by_schema.keys()),
                "connection_info": {
                    "host": self.host,
                    "port": self.port,
                    "database": self.database,
                    "user": self.user
                }
            }
    
    async def _get_table_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de todas las tablas"""
        async with self.pool.acquire() as conn:
            # PostgreSQL tiene estadísticas útiles en pg_stat_user_tables
            stats_query = """
            SELECT 
                schemaname,
                relname as table_name,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples,
                last_vacuum,
                last_analyze
            FROM pg_stat_user_tables
            ORDER BY relname
            """
            
            stats = await conn.fetch(stats_query)
            
            # También obtener tamaños de tablas
            size_query = """
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """
            
            sizes = await conn.fetch(size_query)
            
            return {
                "table_statistics": [dict(row) for row in stats],
                "table_sizes": [dict(row) for row in sizes]
            }
    
    async def _get_indexes_info(self) -> List[Dict[str, Any]]:
        """Obtiene información sobre todos los índices"""
        async with self.pool.acquire() as conn:
            indexes_query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
            """
            
            indexes = await conn.fetch(indexes_query)
            return [dict(row) for row in indexes]
    
    async def _get_table_relationships(self) -> List[Dict[str, Any]]:
        """Obtiene las relaciones entre tablas (foreign keys)"""
        async with self.pool.acquire() as conn:
            fk_query = """
            SELECT
                tc.table_name as source_table,
                kcu.column_name as source_column,
                ccu.table_name as target_table,
                ccu.column_name as target_column,
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
            ORDER BY tc.table_name
            """
            
            relationships = await conn.fetch(fk_query)
            return [dict(row) for row in relationships]
    
    async def _get_columns_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """Obtiene información detallada de todas las columnas por tabla"""
        async with self.pool.acquire() as conn:
            columns_query = """
            SELECT 
                table_name,
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """
            
            columns = await conn.fetch(columns_query)
            
            # Agrupar por tabla
            tables_columns = {}
            for col in columns:
                table_name = col["table_name"]
                if table_name not in tables_columns:
                    tables_columns[table_name] = []
                tables_columns[table_name].append(dict(col))
            
            return tables_columns
    
    # ===== FUNCIONES DE HERRAMIENTAS =====
    
    async def _execute_sql_query(self, query: str, parameters: Optional[List] = None) -> Dict[str, Any]:
        """Ejecuta una consulta SQL personalizada de forma segura"""
        if parameters is None:
            parameters = []
        
        async with self.pool.acquire() as conn:
            # Determinar el tipo de consulta
            query_type = query.strip().upper().split()[0]
            
            if query_type in ['SELECT', 'WITH']:
                # Consulta de lectura
                result = await conn.fetch(query, *parameters)
                return {
                    "query": query,
                    "parameters": parameters,
                    "results": [dict(row) for row in result],
                    "count": len(result),
                    "type": "select"
                }
            else:
                # Consulta de modificación (INSERT, UPDATE, DELETE)
                result = await conn.execute(query, *parameters)
                # result contiene algo como "UPDATE 3" o "INSERT 0 1"
                affected_rows = int(result.split()[-1]) if result.split()[-1].isdigit() else 0
                
                return {
                    "query": query,
                    "parameters": parameters,
                    "affected_rows": affected_rows,
                    "status": result,
                    "type": "modification"
                }
    
    async def _search_table(self, table_name: str, filters: Optional[Dict[str, Any]] = None, 
                          limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Busca registros en una tabla con filtros opcionales"""
        if filters is None:
            filters = {}
        
        # Construir consulta dinámica de forma segura
        base_query = f"SELECT * FROM {table_name}"
        where_clauses = []
        params = []
        param_counter = 1
        
        for column, value in filters.items():
            where_clauses.append(f"{column} = ${param_counter}")
            params.append(value)
            param_counter += 1
        
        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)
        
        base_query += f" LIMIT ${param_counter} OFFSET ${param_counter + 1}"
        params.extend([limit, offset])
        
        async with self.pool.acquire() as conn:
            result = await conn.fetch(base_query, *params)
            
            # También obtener el total de registros que coinciden
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            if where_clauses:
                count_query += " WHERE " + " AND ".join(where_clauses)
            
            total_count = await conn.fetchval(count_query, *params[:-2])  # Sin LIMIT y OFFSET
            
            return {
                "table": table_name,
                "filters": filters,
                "results": [dict(row) for row in result],
                "count": len(result),
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
    
    async def _insert_data(self, table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Inserta uno o múltiples registros en una tabla"""
        
        # Normalizar entrada a lista
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            raise ValueError("No hay datos para insertar")
        
        # Obtener columnas del primer registro
        columns = list(data[0].keys())
        placeholders = ", ".join([f"${i+1}" for i in range(len(columns))])
        
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        async with self.pool.acquire() as conn:
            inserted_count = 0
            
            if len(data) == 1:
                # Insertar un solo registro
                values = [data[0][col] for col in columns]
                await conn.execute(query, *values)
                inserted_count = 1
            else:
                # Insertar múltiples registros usando executemany
                values_list = [[row[col] for col in columns] for row in data]
                await conn.executemany(query, values_list)
                inserted_count = len(data)
            
            return {
                "table": table_name,
                "inserted_count": inserted_count,
                "columns": columns,
                "success": True
            }
    
    async def _update_data(self, table_name: str, set_values: Dict[str, Any], 
                         where_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza registros en una tabla"""
        
        if not set_values:
            raise ValueError("No hay valores para actualizar")
        if not where_conditions:
            raise ValueError("Condiciones WHERE son obligatorias para UPDATE")
        
        # Construir SET clause
        set_clauses = []
        params = []
        param_counter = 1
        
        for column, value in set_values.items():
            set_clauses.append(f"{column} = ${param_counter}")
            params.append(value)
            param_counter += 1
        
        # Construir WHERE clause
        where_clauses = []
        for column, value in where_conditions.items():
            where_clauses.append(f"{column} = ${param_counter}")
            params.append(value)
            param_counter += 1
        
        query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *params)
            affected_rows = int(result.split()[-1]) if result.split()[-1].isdigit() else 0
            
            return {
                "table": table_name,
                "set_values": set_values,
                "where_conditions": where_conditions,
                "affected_rows": affected_rows,
                "success": True
            }
    
    async def _aggregate_data(self, table_name: str, aggregations: List[Dict[str, str]], 
                            group_by: Optional[List[str]] = None, 
                            having: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Realiza agregaciones en los datos.
        
        aggregations: [{"function": "COUNT", "column": "*", "alias": "total"}]
        group_by: ["column1", "column2"]
        having: {"COUNT(*)": {"operator": ">", "value": 10}}
        """
        
        # Construir SELECT clause con agregaciones
        select_parts = []
        for agg in aggregations:
            func = agg["function"].upper()
            column = agg["column"]
            alias = agg.get("alias", f"{func}_{column}")
            select_parts.append(f"{func}({column}) AS {alias}")
        
        # Agregar columnas de GROUP BY al SELECT
        if group_by:
            select_parts = group_by + select_parts
        
        query = f"SELECT {', '.join(select_parts)} FROM {table_name}"
        
        # Agregar GROUP BY
        if group_by:
            query += f" GROUP BY {', '.join(group_by)}"
        
        # Agregar HAVING (simplificado)
        if having:
            having_clauses = []
            for column, condition in having.items():
                operator = condition.get("operator", "=")
                value = condition["value"]
                having_clauses.append(f"{column} {operator} {value}")
            query += f" HAVING {' AND '.join(having_clauses)}"
        
        async with self.pool.acquire() as conn:
            result = await conn.fetch(query)
            
            return {
                "table": table_name,
                "aggregations": aggregations,
                "group_by": group_by,
                "results": [dict(row) for row in result],
                "count": len(result)
            }
    
    async def _export_for_graph(self, query: str, node_label: str, 
                              id_column: str, properties_columns: List[str]) -> Dict[str, Any]:
        """
        Exporta datos en formato adecuado para crear nodos en Neo4j.
        Esta es una función de integración clave con el agente Neo4j.
        """
        
        async with self.pool.acquire() as conn:
            result = await conn.fetch(query)
            
            # Formatear datos para Neo4j
            nodes_data = []
            for row in result:
                node = {
                    "id": str(row[id_column]),  # Convertir a string para compatibilidad
                    "label": node_label,
                    "properties": {}
                }
                
                # Extraer propiedades especificadas
                for prop_col in properties_columns:
                    if prop_col in row:
                        value = row[prop_col]
                        # Convertir tipos Python a tipos compatibles con Neo4j
                        if value is not None:
                            node["properties"][prop_col] = value
                
                nodes_data.append(node)
            
            return {
                "export_type": "neo4j_nodes",
                "node_label": node_label,
                "total_nodes": len(nodes_data),
                "nodes": nodes_data,
                "ready_for_neo4j": True
            }
    
    async def _create_dynamic_table(self, table_name: str, columns: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Crea una tabla nueva con estructura dinámica.
        
        columns: [{"name": "id", "type": "SERIAL PRIMARY KEY"}, {"name": "name", "type": "VARCHAR(100)"}]
        """
        
        # Construir definición de columnas
        column_definitions = []
        for col in columns:
            column_definitions.append(f"{col['name']} {col['type']}")
        
        query = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
        
        async with self.pool.acquire() as conn:
            await conn.execute(query)
            
            return {
                "table_name": table_name,
                "columns": columns,
                "created": True,
                "message": "Tabla creada exitosamente"
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna el estado actual del agente con verificación de conexión real"""
        base_status = await super().get_status()
        
        # Verificar conexión real a PostgreSQL
        connected = False
        connection_details = {}
        
        if self.pool and self.initialized:
            try:
                # Hacer una consulta simple para verificar conectividad
                async with self.pool.acquire() as conn:
                    result = await conn.fetchval("SELECT 1")
                    if result == 1:
                        connected = True
                        connection_details = {
                            "host": self.host,
                            "port": self.port,
                            "database": self.database,
                            "user": self.user,
                            "database_available": True,
                            "pool_size": self.pool.get_size() if hasattr(self.pool, 'get_size') else "unknown"
                        }
            except Exception as e:
                connected = False
                connection_details = {
                    "host": self.host,
                    "port": self.port,
                    "database": self.database,
                    "user": self.user,
                    "error": str(e),
                    "database_available": False
                }
        
        # Agregar información específica de PostgreSQL
        base_status.update({
            "connected": connected,
            "connection_details": connection_details,
            "agent_type": "postgresql",
            "host": self.host,
            "database": self.database
        })
        
        return base_status
    
    async def close(self):
        """Cierra el pool de conexiones"""
        if self.pool:
            await self.pool.close()
            logger.info("Pool de conexiones PostgreSQL cerrado")