# 🚀 Guía de Instalación - Intelligent Data Agents

Esta guía te ayudará a configurar y ejecutar Intelligent Data Agents en tu entorno local.

## 📋 **Prerrequisitos**

### **Software Requerido**
- **Docker** 20.10+ y **Docker Compose** 2.0+
- **Python** 3.11+ (para desarrollo local)
- **Git** (para clonar el repositorio)

### **Cuentas y Servicios**
- **Google Cloud Account** (para Gemini LLM)
- **Neo4j** y **PostgreSQL** (incluidos en docker-compose)

### **Verificar Instalaciones**
```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar Python
python --version
python -m pip --version

# Verificar Git
git --version
```

## 🏗️ **Instalación Básica**

### **1. Clonar Repositorio**
```bash
git clone https://github.com/tu-usuario/intelligent-data-agents.git
cd intelligent-data-agents
```

### **2. Configuración de Entorno**
```bash
# Copiar configuración de ejemplo
cp orchestrator-api/.env.example orchestrator-api/.env

# Editar configuraciones
nano orchestrator-api/.env
```

### **3. Configurar Variables de Entorno**

Edita `orchestrator-api/.env` con tus configuraciones:

```bash
# =============================================================================
# GOOGLE CLOUD & AI
# =============================================================================
GOOGLE_CLOUD_PROJECT=tu-proyecto-gcp
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./vertex-ai-credentials.json
LLM_ENABLED=true

# =============================================================================
# NEO4J CONFIGURATION
# =============================================================================
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=tu-password-neo4j
NEO4J_DATABASE=neo4j

# =============================================================================
# POSTGRESQL CONFIGURATION
# =============================================================================
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=multiagentes
POSTGRES_USER=tu-usuario-postgres
POSTGRES_PASSWORD=tu-password-postgres

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================
ENV=development
PORT=8080
```

### **4. Credenciales de Google Cloud**

```bash
# Descargar credenciales desde Google Cloud Console
# Guardar como: orchestrator-api/vertex-ai-credentials.json

# O usando gcloud CLI
gcloud auth application-default print-access-token
```

### **5. Ejecutar con Docker**
```bash
cd orchestrator-api
docker-compose up -d
```

### **6. Verificar Instalación**
```bash
# Verificar que todos los contenedores estén corriendo
docker-compose ps

# Probar health check
curl http://localhost:8080/health

# Abrir frontend
open http://localhost:8080/static/index.html
```

## 🛠️ **Instalación para Desarrollo**

### **1. Entorno Virtual Python**
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### **2. Instalar Dependencias Python**
```bash
cd orchestrator-api
pip install --upgrade pip
pip install -r requirements.txt
```

### **3. Ejecutar Solo Bases de Datos**
```bash
# Solo bases de datos con Docker
docker-compose up -d neo4j postgres redis
```

### **4. Ejecutar API en Desarrollo**
```bash
# Servidor con hot reload
python main.py

# O usando uvicorn directamente
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### **5. Modo Desarrollo con Volúmenes**
```bash
# Usar docker-compose para desarrollo
docker-compose -f deployment/local-dev/docker-compose.dev.yml up -d
```

## 🧪 **Verificación de Instalación**

### **Script de Verificación Automática**
```bash
# Ejecutar tests de verificación
bash deployment/local-dev/test_deployment.sh
```

### **Verificación Manual**

#### **1. Health Checks**
```bash
# API Health
curl http://localhost:8080/health

# Neo4j (browser)
open http://localhost:7474

# PostgreSQL (pgAdmin)
open http://localhost:5050
```

#### **2. Test de Agentes**
```bash
# Estado de agentes
curl http://localhost:8080/agents/status

# Test consulta simple
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuál es el estado del sistema?"}'
```

#### **3. Test de Conexiones**
```bash
# Test Neo4j
curl -X POST http://localhost:8080/connections/neo4j/test \
  -H "Content-Type: application/json" \
  -d '{
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "tu-password"
  }'

# Test PostgreSQL
curl -X POST http://localhost:8080/connections/postgres/test \
  -H "Content-Type: application/json" \
  -d '{
    "host": "localhost",
    "port": 5432,
    "database": "multiagentes",
    "user": "tu-usuario",
    "password": "tu-password"
  }'
```

## 🌐 **URLs de Acceso**

Una vez instalado correctamente:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Frontend** | http://localhost:8080/static/index.html | - |
| **API Docs** | http://localhost:8080/docs | - |
| **Health Check** | http://localhost:8080/health | - |
| **Neo4j Browser** | http://localhost:7474 | neo4j / tu-password |
| **pgAdmin** | http://localhost:5050 | admin@tecnoandina.cl / tecnoandina |
| **Adminer** | http://localhost:8082 | - |

## 🔧 **Configuraciones Avanzadas**

### **Personalizar Puertos**
```bash
# Cambiar puerto de la API
export PORT=8081
uvicorn main:app --host 0.0.0.0 --port $PORT

# O modificar docker-compose.yml
# ports:
#   - "8081:8080"
```

### **Configurar Bases de Datos Externas**

#### **Neo4j Cloud (AuraDB)**
```bash
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=tu-password-aura
```

#### **PostgreSQL Cloud**
```bash
POSTGRES_HOST=tu-postgres-cloud.com
POSTGRES_PORT=5432
POSTGRES_DB=tu-database
POSTGRES_USER=tu-usuario
POSTGRES_PASSWORD=tu-password
```

### **Configurar Google Cloud**
```bash
# Configurar proyecto
gcloud config set project tu-proyecto-gcp

# Habilitar APIs necesarias
gcloud services enable aiplatform.googleapis.com

# Configurar credenciales
gcloud auth application-default login
```

## 🚨 **Troubleshooting**

### **Problemas Comunes**

#### **1. Puerto 8080 Ocupado**
```bash
# Verificar qué está usando el puerto
lsof -i :8080

# Cambiar puerto
export PORT=8081
docker-compose up -d
```

#### **2. Error de Conexión a Bases de Datos**
```bash
# Verificar estado de contenedores
docker-compose ps

# Ver logs
docker-compose logs neo4j
docker-compose logs postgres

# Reiniciar servicios
docker-compose restart neo4j postgres
```

#### **3. Error de Credenciales Google Cloud**
```bash
# Verificar credenciales
gcloud auth list

# Re-autenticar
gcloud auth application-default login

# Verificar archivo de credenciales
ls -la orchestrator-api/vertex-ai-credentials.json
```

#### **4. Frontend No Carga**
```bash
# Verificar archivos estáticos
ls -la orchestrator-api/static/

# Copiar archivos al contenedor (si es necesario)
docker cp orchestrator-api/static/ container_name:/app/

# Reconstruir imagen
docker-compose build --no-cache mcp-service
```

### **Logs y Debugging**
```bash
# Ver logs de la API
docker-compose logs -f mcp-service

# Ver logs de todas las bases de datos
docker-compose logs neo4j postgres

# Logs en tiempo real
docker-compose logs -f
```

### **Reinicio Completo**
```bash
# Parar todo
docker-compose down

# Limpiar volúmenes (¡CUIDADO: borra datos!)
docker-compose down -v

# Reconstruir todo
docker-compose build --no-cache
docker-compose up -d
```

## 📊 **Verificar Performance**

### **Métricas del Sistema**
```bash
# Uso de recursos
docker stats

# Espacio en disco
docker system df

# Limpiar caché si es necesario
docker system prune
```

### **Test de Carga Básico**
```bash
# Instalar hey (load testing)
go install github.com/rakyll/hey@latest

# Test básico
hey -n 100 -c 10 http://localhost:8080/health
```

## ✅ **Checklist de Instalación**

- [ ] **Docker y Docker Compose** instalados y funcionando
- [ ] **Repositorio clonado** y estructura verificada
- [ ] **Variables de entorno** configuradas en `.env`
- [ ] **Credenciales Google Cloud** configuradas
- [ ] **Contenedores Docker** corriendo correctamente
- [ ] **Health checks** pasando en todos los servicios
- [ ] **Frontend** accesible y funcionando
- [ ] **API endpoints** respondiendo correctamente
- [ ] **Conexiones a bases de datos** exitosas
- [ ] **Consulta de prueba** ejecutada exitosamente

## 🎯 **Próximos Pasos**

1. **Leer documentación de API**: [docs/api/endpoints.md](../api/endpoints.md)
2. **Probar consultas de ejemplo**: [examples/queries/](../../examples/queries/)
3. **Importar colección Postman**: [postman/postman_collection.json](../../postman/postman_collection.json)
4. **Configurar datos de prueba**: [examples/datasets/](../../examples/datasets/)
5. **Desplegar en cloud**: [deployment/cloud-run/](../../deployment/cloud-run/)

---

**¿Problemas con la instalación?** Abre un [issue en GitHub](https://github.com/tu-usuario/intelligent-data-agents/issues) o consulta la [documentación de troubleshooting](./troubleshooting.md).
