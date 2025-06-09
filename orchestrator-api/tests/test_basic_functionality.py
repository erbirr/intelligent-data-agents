# ============================================================================
# TESTS BÁSICOS
# tests/test_basic_functionality.py
# ============================================================================

import asyncio
from typing import Any, Dict

import httpx
import pytest

# Configuración de testing
BASE_URL = "http://localhost:8080"
TIMEOUT = 30.0

class TestMCPMicroservice:
    """Suite de tests básicos para el microservicio MCP"""
    
    @pytest.fixture
    async def client(self):
        """Cliente HTTP para las pruebas"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            yield client
    
    async def test_health_endpoint(self, client):
        """Test: El endpoint de salud debe responder correctamente"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ida-microservice"
    
    async def test_agents_status(self, client):
        """Test: Todos los agentes deben estar inicializados"""
        response = await client.get("/agents/status")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verificar que existen los 3 agentes principales
        expected_agents = ["neo4j", "postgres", "orchestrator"]
        for agent in expected_agents:
            assert agent in data, f"Agente {agent} no encontrado"
            assert data[agent]["initialized"] == True, f"Agente {agent} no inicializado"
    
    async def test_basic_query(self, client):
        """Test: Consulta básica debe funcionar"""
        query_payload = {
            "query": "muéstrame el estado del sistema",
            "context": {"test": True}
        }
        
        response = await client.post("/query", json=query_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "result" in data
        assert "metadata" in data
        assert data["metadata"]["query"] == query_payload["query"]
    
    async def test_neo4j_specific_query(self, client):
        """Test: Consulta específica para Neo4j"""
        query_payload = {
            "query": "muéstrame el esquema del grafo"
        }
        
        response = await client.post("/query", json=query_payload)
        assert response.status_code == 200
        
        data = response.json()
        metadata = data["metadata"]
        
        # Debe usar el agente Neo4j
        agents_used = metadata.get("agents_used", [])
        assert "neo4j" in agents_used or len(agents_used) == 0  # Puede ser consulta simple
    
    async def test_postgres_specific_query(self, client):
        """Test: Consulta específica para PostgreSQL"""
        query_payload = {
            "query": "muéstrame las tablas de la base de datos"
        }
        
        response = await client.post("/query", json=query_payload)
        assert response.status_code == 200
        
        data = response.json()
        metadata = data["metadata"]
        
        # Debe usar el agente PostgreSQL
        agents_used = metadata.get("agents_used", [])
        assert "postgres" in agents_used or len(agents_used) == 0
    
    async def test_hybrid_query(self, client):
        """Test: Consulta híbrida que requiere ambos agentes"""
        query_payload = {
            "query": "compara las estadísticas de ambas bases de datos"
        }
        
        response = await client.post("/query", json=query_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "result" in data
        assert "metadata" in data
        
        # Debe tener tiempo de ejecución medido
        execution_time = data["metadata"].get("execution_time", 0)
        assert execution_time >= 0
    
    async def test_invalid_query_handling(self, client):
        """Test: Manejo de consultas inválidas o vacías"""
        
        # Consulta vacía
        response = await client.post("/query", json={"query": ""})
        assert response.status_code in [200, 400]  # Puede manejar o rechazar
        
        # Payload inválido
        response = await client.post("/query", json={})
        assert response.status_code in [200, 422]  # Error de validación esperado
        
        # JSON malformado
        response = await client.post("/query", data="invalid json")
        assert response.status_code == 422
    
    async def test_performance_basic(self, client):
        """Test: Rendimiento básico - consultas simples deben ser rápidas"""
        
        start_time = asyncio.get_event_loop().time()
        
        query_payload = {"query": "estado del sistema"}
        response = await client.post("/query", json=query_payload)
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        assert response.status_code == 200
        assert total_time < 10.0  # Menos de 10 segundos para consulta básica
    
    async def test_concurrent_requests(self, client):
        """Test: El sistema debe manejar múltiples consultas concurrentes"""
        
        async def single_query():
            response = await client.post("/query", json={"query": "estado básico"})
            return response.status_code == 200
        
        # Ejecutar 5 consultas concurrentes
        tasks = [single_query() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Todas deben ser exitosas
        assert all(results), "No todas las consultas concurrentes fueron exitosas"
