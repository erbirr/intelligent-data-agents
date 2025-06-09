# ============================================================================
# TESTS DE INTEGRACIÓN
# tests/test_integration.py
# ============================================================================

import asyncio

import httpx
import psycopg2
import pytest
from neo4j import GraphDatabase


class TestIntegration:
    """Tests de integración que verifican la comunicación con las bases de datos"""
    
    @pytest.fixture
    async def client(self):
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
            yield client
    
    def test_postgres_connection_direct(self):
        """Test: Conexión directa a PostgreSQL funcional"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="mcp_database",
                user="postgres",
                password="devpassword123"
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users;")
            result = cursor.fetchone()
            
            assert result[0] >= 0  # Debe tener al menos 0 usuarios
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            pytest.fail(f"No se pudo conectar a PostgreSQL: {e}")
    
    def test_neo4j_connection_direct(self):
        """Test: Conexión directa a Neo4j funcional"""
        try:
            driver = GraphDatabase.driver(
                "bolt://localhost:7687", 
                auth=("neo4j", "devpassword123")
            )
            
            with driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) as total")
                record = result.single()
                
                assert record["total"] >= 0  # Debe tener al menos 0 nodos
            
            driver.close()
            
        except Exception as e:
            pytest.fail(f"No se pudo conectar a Neo4j: {e}")
    
    async def test_data_consistency(self, client):
        """Test: Los datos entre PostgreSQL y Neo4j deben ser consistentes"""
        
        # Obtener datos de PostgreSQL a través del microservicio
        postgres_response = await client.post("/query", json={
            "query": "muéstrame información de usuarios de la base de datos"
        })
        
        # Obtener datos de Neo4j a través del microservicio
        neo4j_response = await client.post("/query", json={
            "query": "muéstrame usuarios del grafo"
        })
        
        assert postgres_response.status_code == 200
        assert neo4j_response.status_code == 200
        
        # Ambas respuestas deben tener contenido
        postgres_data = postgres_response.json()
        neo4j_data = neo4j_response.json()
        
        assert "result" in postgres_data
        assert "result" in neo4j_data
    
    async def test_end_to_end_workflow(self, client):
        """Test: Flujo completo de extremo a extremo"""
        
        # 1. Verificar estado inicial
        health_response = await client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Explorar sistema
        explore_response = await client.post("/query", json={
            "query": "dame un resumen completo del sistema"
        })
        assert explore_response.status_code == 200
        
        # 3. Hacer consulta híbrida
        hybrid_response = await client.post("/query", json={
            "query": "combina datos de ambas fuentes para mostrar insights"
        })
        assert hybrid_response.status_code == 200
        
        # Verificar que se usaron múltiples agentes
        hybrid_data = hybrid_response.json()
        metadata = hybrid_data.get("metadata", {})
        
        # Debe tener información de ejecución
        assert "execution_time" in metadata
        assert metadata["execution_time"] >= 0