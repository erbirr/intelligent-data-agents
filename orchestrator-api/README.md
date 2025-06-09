# 🎯 Orchestrator API

Este directorio contiene el **servicio principal** de Intelligent Data Agents - una API REST construida con FastAPI que orquesta agentes inteligentes para Neo4j, PostgreSQL y Gemini LLM.

## 📁 **Estructura del Directorio**

```
orchestrator-api/
├── agents/                     # 🤖 Agentes MCP
│   ├── __init__.py
│   ├── neo4j_agent.py         # Agente especializado en Neo4j
│   ├── postgres_agent.py      # Agente especializado en PostgreSQL
│   └── orchestrator.py        # Orquestador principal
├── llm/                        # 🧠 Integración LLM
│   ├── __init__.py
│   ├── gemini_client.py        # Cliente Vertex AI Gemini
│   └── pattern_analyzer.py    # Análisis inteligente de patrones
├── mcp/                        # 🔗 Protocolo MCP base
│   ├── __init__.py
│   └── base.py                 # Clases base MCP
├── static/                     # 🌐 Frontend Web
│   ├── index.html              # Interfaz principal
│   ├── css/
│   │   └── style.css           # Estilos CSS
│   └── js/
│       └── app.js              # JavaScript de la aplicación
├── tests/                      # 🧪 Tests unitarios
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_api.py
│   └── test_llm.py
├── main.py                     # 🚀 API principal FastAPI
├── requirements.txt            # 📦 Dependencias Python
├── Dockerfile                  # 🐳 Imagen Docker
├── docker-compose.yml          # 🔧 Stack completo
├── .env.example               # ⚙️ Variables de entorno ejemplo
├── .env                       # ⚙️ Variables de entorno (local)
├── .dockerignore              # 🚫 Exclusiones Docker
└── README.md                  # 📖 Este archivo
```

## 🚀 **Inicio Rápido**

### **Opción 1: Docker (Recomendada)**

```bash
# 1. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus configuraciones

# 2. Ejecutar stack completo
docker-compose up -d

# 3. Verificar estado
docker-compose ps

# 4. Acceder a la aplicación
open http://localhost:8080/static/index.html
```

### **Opción 2: Desarrollo Local**

```bash
# 1. Entorno virtual
python -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar entorno
cp .env.example .env
# Editar .env con configuraciones

# 4. Ejecutar solo bases de datos
docker-compose up -d neo4j postgres redis

# 5. Ejecutar API
python main.py
```

## 🔧 **Configuración**

### **Variables de Entorno Críticas**

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=tu-proyecto
GOOGLE_APPLICATION_CREDENTIALS=./vertex-ai-credentials.json

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=tu-password

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=tu-database
POSTGRES_USER=tu-usuario
POSTGRES_PASSWORD=tu-password

# Sistema
ENV=development
LLM_ENABLED=true
PORT=8080
```

## 📡 **Endpoints Principales**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información de la API |
| `/health` | GET | Health check del sistema |
| `/docs` | GET | Documentación interactiva |
| `/query` | POST | Consultas inteligentes |
| `/agents/status` | GET | Estado de agentes |
| `/connections/neo4j/test` | POST | Test conexión Neo4j |
| `/connections/postgres/test` | POST | Test conexión PostgreSQL |

## 🤖 **Agentes Disponibles**

### **🔗 Neo4j Agent**
- **Especialidad**: Análisis de grafos y relaciones
- **Herramientas**: 5 herramientas MCP
- **Recursos**: 4 recursos disponibles

### **🗄️ PostgreSQL Agent**
- **Especialidad**: Consultas relacionales y agregaciones
- **Herramientas**: 7 herramientas MCP
- **Recursos**: 5 recursos disponibles

### **🧠 Orchestrator Agent**
- **Especialidad**: Coordinación y routing inteligente
- **LLM**: Gemini 1.5 Pro para análisis de consultas

## 🧪 **Testing**

```bash
# Tests unitarios
pytest tests/

# Health check
curl http://localhost:8080/health

# Test consulta
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuál es el estado del sistema?"}'
```

## 🐳 **Docker**

```bash
# Desarrollo
docker-compose up -d

# Logs
docker-compose logs -f mcp-service

# Desarrollo con hot reload
docker-compose -f ../deployment/local-dev/docker-compose.dev.yml up -d
```

## 📚 **Documentación Adicional**

- **[API Endpoints](../docs/api/endpoints.md)**: Documentación completa de la API
- **[Installation Guide](../docs/setup/installation.md)**: Guía de instalación detallada
- **[Query Examples](../examples/queries/)**: Ejemplos de consultas por tipo
- **[Main Project README](../README.md)**: Documentación principal del proyecto

---

**Version**: 1.0.0  
**Last Updated**: 2025-06-04
