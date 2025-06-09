# main.py - Punto de entrada del microservicio
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from agents.neo4j_agent import Neo4jAgent
from agents.orchestrator import OrchestratorAgent
from agents.postgres_agent import PostgresAgent
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancias globales de los agentes
orchestrator = None
neo4j_agent = None
postgres_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    global orchestrator, neo4j_agent, postgres_agent
    
    # STARTUP
    logger.info("Iniciando microservicio MCP...")
    
    try:
        # Inicializar agentes de base de datos
        neo4j_agent = Neo4jAgent(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "tecnoandina"),
            database=os.getenv("NEO4J_DATABASE", "multiagentes")
        )
        
        postgres_agent = PostgresAgent(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "testdb"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password")
        )
        
        # Inicializar orquestador con referencias a los otros agentes
        orchestrator = OrchestratorAgent(
            neo4j_agent=neo4j_agent,
            postgres_agent=postgres_agent
        )
        
        # Inicializar todos los agentes
        await neo4j_agent.initialize()
        await postgres_agent.initialize()
        await orchestrator.initialize()
        
        logger.info("Todos los agentes inicializados correctamente")
        
    except Exception as e:
        logger.error(f"Error durante la inicialización: {e}")
        # Los agentes pueden fallar en inicialización pero la API debe seguir funcionando
    
    yield  # Aquí la aplicación está funcionando
    
    # SHUTDOWN
    logger.info("Cerrando microservicio MCP...")
    
    try:
        if orchestrator:
            await orchestrator.close()
        if neo4j_agent:
            await neo4j_agent.close()
        if postgres_agent:
            await postgres_agent.close()
        
        logger.info("Todas las conexiones cerradas correctamente")
    except Exception as e:
        logger.error(f"Error durante el cierre: {e}")

# Crear aplicación FastAPI con documentación y lifespan
app = FastAPI(
    title="MCP Microservice - Agentes Inteligentes",
    description="API REST para sistema de agentes MCP con Neo4j, PostgreSQL y Gemini LLM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos del frontend
if os.path.exists("./static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelos de request/response mejorados
class QueryRequest(BaseModel):
    query: str = Field(..., description="Consulta en lenguaje natural", example="¿Cuántos usuarios están registrados?")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Contexto adicional para la consulta")
    neo4j_config: Optional[Dict[str, str]] = Field(default=None, description="Configuración dinámica de Neo4j")
    postgres_config: Optional[Dict[str, str]] = Field(default=None, description="Configuración dinámica de PostgreSQL")

class QueryResponse(BaseModel):
    result: Any = Field(..., description="Resultado de la consulta")
    metadata: Dict[str, Any] = Field(..., description="Metadatos del procesamiento")
    execution_time: Optional[float] = Field(default=None, description="Tiempo de ejecución en segundos")
    
class Neo4jConnectionConfig(BaseModel):
    uri: str = Field(..., example="bolt://localhost:7687")
    user: str = Field(..., example="neo4j")
    password: str = Field(..., example="password")
    database: Optional[str] = Field(default="mmultiagentes", example="neo4j")

class PostgresConnectionConfig(BaseModel):
    host: str = Field(..., example="localhost")
    port: int = Field(default=5432, example=5432)
    database: str = Field(..., example="postgres")
    user: str = Field(..., example="postgres")
    password: str = Field(..., example="password")

class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

# Instancias globales de los agentes
orchestrator = None
neo4j_agent = None
postgres_agent = None

@app.on_event("startup")
async def startup_event():
    """Inicializa todos los agentes al arrancar el servicio"""
    global orchestrator, neo4j_agent, postgres_agent
    
    logger.info("Iniciando microservicio MCP...")
    
    # Inicializar agentes de base de datos
    neo4j_agent = Neo4jAgent(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "tecnoandina"),
        database=os.getenv("NEO4J_DATABASE", "multiagentes")
    )
    
    postgres_agent = PostgresAgent(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "testdb"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "password")
    )
    
    # Inicializar orquestador con referencias a los otros agentes
    orchestrator = OrchestratorAgent(
        neo4j_agent=neo4j_agent,
        postgres_agent=postgres_agent
    )
    
    # Inicializar todos los agentes
    await neo4j_agent.initialize()
    await postgres_agent.initialize()
    await orchestrator.initialize()
    
    logger.info("Todos los agentes inicializados correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Cierra las conexiones al terminar el servicio"""
    global orchestrator, neo4j_agent, postgres_agent
    
    logger.info("Cerrando microservicio MCP...")
    
    if orchestrator:
        await orchestrator.close()
    if neo4j_agent:
        await neo4j_agent.close()
    if postgres_agent:
        await postgres_agent.close()

@app.get("/")
async def root():
    """Página principal - redirigir al frontend"""
    return {"message": "IDA Microservices API", "docs": "/docs", "frontend": "/static/index.html"}

@app.get("/health")
async def health_check():
    """Endpoint de salud para Cloud Run"""
    return {
        "status": "healthy", 
        "service": "ida-microservices",
        "version": "1.0.0",
        "agents": {
            "neo4j": neo4j_agent is not None,
            "postgres": postgres_agent is not None,
            "orchestrator": orchestrator is not None
        }
    }

@app.post("/connections/neo4j/test", response_model=ConnectionTestResponse)
async def test_neo4j_connection(config: Neo4jConnectionConfig):
    """Probar conexión a Neo4j con configuración personalizada"""
    try:
        # Crear agente temporal para test
        test_agent = Neo4jAgent(
            uri=config.uri,
            user=config.user, 
            password=config.password,
            database=config.database
        )
        
        await test_agent.initialize()
        status = await test_agent.get_status()
        await test_agent.close()
        
        return ConnectionTestResponse(
            success=True,
            message="Conexión exitosa a Neo4j",
            details=status
        )
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"Error conectando a Neo4j: {str(e)}"
        )

@app.post("/connections/postgres/test", response_model=ConnectionTestResponse)
async def test_postgres_connection(config: PostgresConnectionConfig):
    """Probar conexión a PostgreSQL con configuración personalizada"""
    try:
        # Crear agente temporal para test
        test_agent = PostgresAgent(
            host=config.host,
            port=config.port,
            database=config.database,
            user=config.user,
            password=config.password
        )
        
        await test_agent.initialize()
        status = await test_agent.get_status()
        await test_agent.close()
        
        return ConnectionTestResponse(
            success=True,
            message="Conexión exitosa a PostgreSQL",
            details=status
        )
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"Error conectando a PostgreSQL: {str(e)}"
        )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Procesa una consulta a través del orquestador.
    El orquestador decide qué agentes involucrar según la consulta.
    
    Soporta configuración dinámica de conexiones para cada consulta.
    """
    import time
    start_time = time.time()
    
    try:
        # Usar orquestador global o crear uno temporal con nuevas conexiones
        current_orchestrator = orchestrator
        temp_agents = []
        
        # Si se proporcionan configuraciones personalizadas, crear agentes temporales
        if request.neo4j_config or request.postgres_config:
            temp_neo4j = None
            temp_postgres = None
            
            if request.neo4j_config:
                temp_neo4j = Neo4jAgent(**request.neo4j_config)
                await temp_neo4j.initialize()
                temp_agents.append(temp_neo4j)
            
            if request.postgres_config:
                temp_postgres = PostgresAgent(**request.postgres_config)
                await temp_postgres.initialize()
                temp_agents.append(temp_postgres)
            
            # Crear orquestador temporal
            if temp_neo4j or temp_postgres:
                current_orchestrator = OrchestratorAgent(
                    neo4j_agent=temp_neo4j or neo4j_agent,
                    postgres_agent=temp_postgres or postgres_agent
                )
                await current_orchestrator.initialize()
                temp_agents.append(current_orchestrator)
        
        if not current_orchestrator:
            raise HTTPException(status_code=500, detail="Orquestador no disponible")
        
        logger.info(f"Procesando consulta: {request.query}")
        result = await current_orchestrator.process_query(request.query, request.context)
        
        # Limpiar agentes temporales
        for agent in temp_agents:
            try:
                await agent.close()
            except:
                pass
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            result=result["data"], 
            metadata=result["metadata"],
            execution_time=execution_time
        )
    
    except Exception as e:
        # Limpiar agentes temporales en caso de error
        for agent in temp_agents:
            try:
                await agent.close()
            except:
                pass
                
        logger.error(f"Error procesando consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/status")
async def get_agents_status():
    """Retorna el estado de todos los agentes"""
    status = {}
    
    try:
        if neo4j_agent:
            status["neo4j"] = await neo4j_agent.get_status()
        else:
            status["neo4j"] = {"connected": False, "message": "No inicializado"}
            
        if postgres_agent:
            status["postgres"] = await postgres_agent.get_status()
        else:
            status["postgres"] = {"connected": False, "message": "No inicializado"}
            
        if orchestrator:
            status["orchestrator"] = await orchestrator.get_status()
        else:
            status["orchestrator"] = {"connected": False, "message": "No inicializado"}
    except Exception as e:
        logger.error(f"Error obteniendo estado de agentes: {e}")
        status["error"] = str(e)
    
    return status

@app.get("/agents/capabilities")
async def get_agents_capabilities():
    """Retorna las capacidades disponibles de todos los agentes"""
    capabilities = {}
    
    try:
        if orchestrator and hasattr(orchestrator, 'available_capabilities'):
            capabilities = orchestrator.available_capabilities
        else:
            capabilities = {
                "neo4j": ["graph_queries", "relationship_analysis", "pattern_matching"],
                "postgres": ["sql_queries", "data_aggregation", "analytics"],
                "orchestrator": ["query_routing", "multi_agent_coordination", "result_synthesis"]
            }
    except Exception as e:
        logger.error(f"Error obteniendo capacidades: {e}")
        capabilities["error"] = str(e)
    
    return capabilities

@app.get("/system/info")
async def get_system_info():
    """Información del sistema y configuración"""
    return {
        "service": "IDA Microservices",
        "version": "1.0.0",
        "environment": os.getenv("ENV", "development"),
        "cloud_project": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "region": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        "llm_enabled": os.getenv("LLM_ENABLED", "true").lower() == "true",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "docs": "/docs",
            "frontend": "/static/index.html"
        }
    }

if __name__ == "__main__":
    # Para desarrollo local
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", "8080")),
        reload=True
    )