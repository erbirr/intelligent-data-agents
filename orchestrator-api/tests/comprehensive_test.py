#!/usr/bin/env python3
"""
Script de pruebas comprehensivo para el microservicio MCP.
Ejecuta una batería completa de tests para verificar todas las funcionalidades.
"""

import asyncio
import json
import time
from typing import Any, Dict, List

import httpx


async def test_comprehensive_mcp_system():
    """Ejecuta una batería completa de pruebas del Universo MCP"""
    
    print("🧪 INICIANDO PRUEBAS COMPREHENSIVAS DEL UNIVERSO MCP")
    print("=" * 60)
    
    base_url = "http://localhost:8080"
    
    # Lista de pruebas a ejecutar
    test_queries = [
        {
            "name": "Exploración de Neo4j",
            "query": "muéstrame el esquema del grafo",
            "expected_agents": ["neo4j"],
            "description": "Verifica que el agente Neo4j responde correctamente"
        },
        {
            "name": "Exploración de PostgreSQL", 
            "query": "muéstrame las tablas de la base de datos",
            "expected_agents": ["postgres"],
            "description": "Verifica que el agente PostgreSQL responde correctamente"
        },
        {
            "name": "Consulta Híbrida Simple",
            "query": "compara estadísticas de ambas bases de datos",
            "expected_agents": ["neo4j", "postgres"],
            "description": "Verifica que el orquestador puede combinar múltiples fuentes"
        },
        {
            "name": "Análisis Complejo",
            "query": "dame un resumen completo del sistema incluyendo capacidades y datos disponibles",
            "expected_agents": None,  # Puede usar cualquier combinación
            "description": "Prueba capacidades de análisis avanzado del orquestador"
        },
        {
            "name": "Consulta Ambigua",
            "query": "información general",
            "expected_agents": None,
            "description": "Verifica cómo maneja consultas vagas"
        }
    ]
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        results = []
        
        for i, test in enumerate(test_queries, 1):
            print(f"\n🔍 Prueba {i}/5: {test['name']}")
            print(f"📝 Descripción: {test['description']}")
            print(f"🗣️  Consulta: '{test['query']}'")
            
            try:
                start_time = time.time()
                
                response = await client.post("/query", json={
                    "query": test["query"],
                    "context": {"test_id": f"comprehensive_test_{i}"}
                })
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    metadata = data.get("metadata", {})
                    agents_used = metadata.get("agents_used", [])
                    strategy = metadata.get("strategy", "unknown")
                    
                    print(f"✅ Respuesta exitosa (tiempo: {execution_time:.2f}s)")
                    print(f"🤖 Agentes utilizados: {agents_used}")
                    print(f"📊 Estrategia: {strategy}")
                    
                    # Verificar agentes esperados si se especificaron
                    if test["expected_agents"]:
                        if any(agent in agents_used for agent in test["expected_agents"]):
                            print(f"✅ Agentes esperados detectados correctamente")
                        else:
                            print(f"⚠️  Agentes esperados {test['expected_agents']} no detectados")
                    
                    results.append({
                        "test": test["name"],
                        "success": True,
                        "execution_time": execution_time,
                        "agents_used": agents_used,
                        "strategy": strategy
                    })
                    
                else:
                    print(f"❌ Error HTTP: {response.status_code}")
                    results.append({
                        "test": test["name"],
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"❌ Error en prueba: {e}")
                results.append({
                    "test": test["name"],
                    "success": False,
                    "error": str(e)
                })
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS COMPREHENSIVAS")
        print("=" * 60)
        
        successful_tests = sum(1 for r in results if r["success"])
        total_tests = len(results)
        
        print(f"✅ Pruebas exitosas: {successful_tests}/{total_tests}")
        
        if successful_tests == total_tests:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON! Tu sistema MCP está funcionando perfectamente.")
        else:
            print(f"⚠️  {total_tests - successful_tests} pruebas fallaron. Revisa los detalles arriba.")
        
        # Estadísticas de rendimiento
        execution_times = [r.get("execution_time", 0) for r in results if r["success"]]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            print(f"⏱️  Tiempo promedio de respuesta: {avg_time:.2f}s")
            print(f"⏱️  Tiempo máximo de respuesta: {max_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_mcp_system())