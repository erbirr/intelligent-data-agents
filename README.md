# 🤖 Intelligent Data Agents

> **AI-powered orchestration system for Neo4j and PostgreSQL with natural language queries using Gemini LLM**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-Ready-orange.svg)](https://cloud.google.com/run)

## 🎯 **Descripción**

**Intelligent Data Agents** es un sistema avanzado de orquestación que unifica el acceso a bases de datos **Neo4j** (grafos) y **PostgreSQL** (relacional) a través de agentes inteligentes powered por **Gemini LLM**. Permite realizar consultas en **lenguaje natural** que son automáticamente dirigidas a la base de datos apropiada o combinadas inteligentemente.

### ✨ **Características Principales**

- 🧠 **Orquestador Inteligente**: Analiza consultas en lenguaje natural con Gemini LLM
- 📊 **Agente Neo4j**: Especializado en análisis de grafos y relaciones
- 🗄️ **Agente PostgreSQL**: Optimizado para consultas relacionales y agregaciones  
- 🔄 **Consultas Híbridas**: Combina datos de ambas bases automáticamente
- 🌐 **API REST**: FastAPI con documentación automática
- 💻 **Frontend Web**: Interfaz moderna para configuración y consultas
- ☁️ **Cloud Ready**: Desplegable en Google Cloud Run
- 🐳 **Docker**: Desarrollo local completo con docker-compose

## 🏗️ **Arquitectura del Sistema**

```
[Usuario] → [Frontend Web] → [API REST FastAPI] → [Orquestador Gemini]
                                                        ↓
                                               [Agente Neo4j] ←→ [Neo4j DB]
                                                        ↓
                                             [Agente PostgreSQL] ←→ [PostgreSQL DB]
```

## 🚀 **Inicio Rápido**

### **Prerequisitos**

- Docker & Docker Compose
- Python 3.11+ (para desarrollo local)
- Cuenta Google Cloud (para Gemini LLM)
- Neo4j y PostgreSQL (incluidos en docker-compose)

### **1. Clonar Repositorio**

```bash
git clone https://github.com/tu-usuario/intelligent-data-agents.git
cd intelligent-data-agents
```

### **2. Configuración Rápida**

```bash
# Copiar configuración de ejemplo
cp orchestrator-api/.env.example orchestrator-api/.env

# Editar configuraciones (Neo4j, PostgreSQL, Google Cloud)
nano orchestrator-api/.env
```

### **3. Ejecutar con Docker**

```bash
cd orchestrator-api
docker-compose up -d
```

### **4. Acceder a la Aplicación**

- **🌐 Frontend**: http://localhost:8080/static/index.html
- **📚 API Docs**: http://localhost:8080/docs  
- **❤️ Health Check**: http://localhost:8080/health
- **🔍 Neo4j Browser**: http://localhost:7474
- **🔧 pgAdmin**: http://localhost:5050

## 📋 **Ejemplos de Uso**

### **Consultas de Grafo (Neo4j)**
```
"¿Qué productos están más conectados entre sí?"
"Muestra las relaciones entre usuarios y productos"
"Encuentra caminos cortos entre entidades"
```

### **Consultas Relacionales (PostgreSQL)**
```
"Dame el promedio de ventas por mes"
"Cuenta total de registros por categoría" 
"Métricas de rendimiento agregadas"
```

### **Consultas Híbridas**
```
"Combina patrones de navegación con compras históricas"
"Enriquece datos relacionales con análisis de grafo"
"Detecta anomalías usando ambas fuentes"
```

## 📁 **Estructura del Proyecto**

```
intelligent-data-agents/
├── orchestrator-api/              # 🎯 Servicio principal FastAPI
│   ├── agents/                    # Agentes MCP (Neo4j, PostgreSQL, Orchestrator)
│   ├── llm/                       # Integración Gemini LLM
│   ├── static/                    # Frontend Web
│   ├── mcp/                       # Protocolo MCP base
│   ├── tests/                     # Tests unitarios
│   ├── main.py                    # API principal
│   ├── Dockerfile                 # Imagen Docker
│   └── docker-compose.yml         # Stack completo
├── deployment/                    # 🚀 Scripts de despliegue
│   ├── cloud-run/                 # Google Cloud Run
│   ├── kubernetes/                # Kubernetes (futuro)
│   └── local-dev/                 # Desarrollo local
├── docs/                          # 📚 Documentación
│   ├── api/                       # Documentación API
│   ├── setup/                     # Guías de configuración
│   └── examples/                  # Ejemplos detallados
├── examples/                      # 💡 Ejemplos de uso
│   ├── queries/                   # Consultas de ejemplo
│   ├── datasets/                  # Datos de prueba
│   └── notebooks/                 # Jupyter notebooks
├── postman/                       # 🧪 Testing
│   └── collections/               # Colecciones Postman
├── .github/workflows/             # 🔄 CI/CD
└── README.md                      # 📖 Este archivo
```

## 🛠️ **Desarrollo**

### **Configuración Local**

```bash
# 1. Entorno virtual Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Instalar dependencias
cd orchestrator-api
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 4. Ejecutar solo bases de datos
docker-compose up -d neo4j postgres redis

# 5. Ejecutar API en desarrollo
python main.py
```

### **Testing**

```bash
# Tests unitarios
pytest tests/

# Tests de integración con Postman
# Importar: postman/collections/ida-microservice.json

# Tests automatizados
bash deployment/local-dev/test_deployment.sh
```

## ☁️ **Despliegue en Producción**

### **Google Cloud Run**

```bash
# Configuración automática
cd deployment/cloud-run
./setup_gcp.sh

# Despliegue
./deploy.sh
```

### **Docker Local**

```bash
cd orchestrator-api
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 **Configuración**

### **Variables de Entorno Principales**

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
ENV=production
LLM_ENABLED=true
PORT=8080
```

## 🤝 **Contribuir**

1. Fork el proyecto
2. Crear branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📊 **Roadmap**

- [ ] **v1.1**: Soporte para más bases de datos (MongoDB, Cassandra)
- [ ] **v1.2**: Interface de administración avanzada
- [ ] **v1.3**: Métricas y monitoring avanzado
- [ ] **v1.4**: Soporte para Kubernetes
- [ ] **v2.0**: Multi-tenancy y autenticación avanzada

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🔗 **Enlaces Útiles**

- **📚 Documentación Completa**: [docs/](docs/)
- **🧪 Ejemplos**: [examples/](examples/)
- **🚀 Guía de Despliegue**: [deployment/](deployment/)
- **📫 Issues**: [GitHub Issues](https://github.com/tu-usuario/intelligent-data-agents/issues)

## 👥 **Equipo**

- **Desarrollador Principal**: Tu Nombre
- **Empresa**: Tecnoandina
- **Contacto**: tu-email@tecnoandina.cl

---

<p align="center">
  <strong>Hecho con ❤️ usando FastAPI, Neo4j, PostgreSQL y Gemini LLM</strong>
</p>
