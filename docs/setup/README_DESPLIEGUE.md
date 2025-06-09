# 🚀 Guía Completa de Despliegue - Sistema MCP

## 📋 Resumen del Proyecto

El **Sistema MCP (Multi-agent Communication Protocol)** es una solución de agentes inteligentes que integra:

- **🧠 Orquestador Inteligente**: Usa Gemini LLM para dirigir consultas
- **📊 Agente Neo4j**: Especializado en análisis de grafos y relaciones
- **🗄️ Agente PostgreSQL**: Optimizado para consultas relacionales y agregaciones
- **🌐 API REST**: FastAPI con endpoints robustos
- **💻 Frontend**: Interfaz web moderna y responsiva
- **☁️ Cloud Ready**: Optimizado para Google Cloud Run

## 🏗️ Arquitectura del Sistema

```
[Frontend] → [API REST] → [Orquestador] → [Agente Neo4j]
                                      → [Agente PostgreSQL]
                                      → [Gemini LLM]
```

## 🛠️ Configuración del Proyecto GCP

### Información del Proyecto
- **Nombre**: tecnoandina
- **ID del Proyecto**: `prj-ia-tecnoandina`
- **Cuenta**: erbi.ramirez@tecnoandina.cl
- **Región por Defecto**: us-central1
- **Zona por Defecto**: us-central1-a

### Variables de Entorno Críticas
```bash
export GOOGLE_CLOUD_PROJECT=prj-ia-tecnoandina
export GOOGLE_CLOUD_REGION=us-central1
export GOOGLE_APPLICATION_CREDENTIALS=./vertex-ai-credentials.json
```

## 🚀 Opciones de Despliegue

### Opción 1: Despliegue Automático (Recomendado)

```bash
# 1. Clonar/ubicarse en el directorio del proyecto
cd ida-microservice

# 2. Configurar proyecto GCP
gcloud config set project prj-ia-tecnoandina
gcloud config set compute/region us-central1

# 3. Ejecutar despliegue completo
./deploy.sh

# 4. Acceder a la aplicación
# La URL se mostrará al final del despliegue
```

### Opción 2: Despliegue Manual Paso a Paso

```bash
# 1. Habilitar APIs necesarias
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  aiplatform.googleapis.com

# 2. Construir imagen
docker build -t gcr.io/prj-ia-tecnoandina/ida-microservice .

# 3. Subir imagen
docker push gcr.io/prj-ia-tecnoandina/ida-microservice

# 4. Desplegar a Cloud Run
gcloud run deploy ida-microservice \
  --image=gcr.io/prj-ia-tecnoandina/ida-microservice \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --max-instances=10 \
  --port=8080 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=prj-ia-tecnoandina,GOOGLE_CLOUD_LOCATION=us-central1,ENV=production"
```

### Opción 3: Usando Cloud Build

```bash
# Despliegue con Cloud Build (CI/CD)
gcloud builds submit --config cloudbuild.yaml .
```

## 🔧 Configuración Local para Desarrollo

### Prerrequisitos
- Docker
- Python 3.11+
- gcloud CLI
- Credenciales de GCP configuradas

### Ejecutar Localmente

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Ejecutar con Docker
docker-compose up -d

# 4. Ejecutar servidor de desarrollo
python main.py

# 5. Acceder a la aplicación
# Frontend: http://localhost:8080/static/index.html
# API Docs: http://localhost:8080/docs
```

## 🌐 Endpoints de la API

### Principales
- `GET /` - Información de la API
- `GET /health` - Estado del sistema
- `POST /query` - Consultas inteligentes
- `GET /agents/status` - Estado de agentes

### Configuración
- `POST /connections/neo4j/test` - Probar Neo4j
- `POST /connections/postgres/test` - Probar PostgreSQL

### Monitoreo
- `GET /system/info` - Información del sistema
- `GET /agents/capabilities` - Capacidades de agentes

## 📱 Uso del Frontend

### Acceso
- **Local**: http://localhost:8080/static/index.html
- **Cloud Run**: https://[SERVICE-URL]/static/index.html

### Funcionalidades
1. **Configurar Conexiones**: Neo4j y PostgreSQL
2. **Probar Conexiones**: Verificar configuraciones
3. **Consultas Inteligentes**: Lenguaje natural
4. **Ver Resultados**: Tablas y JSON
5. **Monitoreo**: Estado de agentes

### Ejemplos de Consultas
- "¿Cuántos usuarios están conectados entre sí?"
- "Dame el promedio de ventas por mes"
- "Encuentra productos relacionados en el grafo"
- "Combina datos de relaciones con estadísticas"

## 🧪 Testing con Postman

### Importar Colección
1. Abrir Postman
2. Importar `postman_collection.json`
3. Configurar variables de entorno:
   - `base_url`: URL de tu servicio
   - Credenciales de bases de datos

### Flujo de Testing Recomendado
1. **Health Check** - Verificar que el servicio esté activo
2. **Test Connections** - Probar conexiones a bases de datos
3. **Simple Queries** - Consultas básicas
4. **Complex Queries** - Consultas avanzadas e híbridas

## 🔒 Seguridad y Configuración

### Variables de Entorno Críticas
```bash
# Proyecto GCP
GOOGLE_CLOUD_PROJECT=prj-ia-tecnoandina
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./vertex-ai-credentials.json

# Neo4j (configurar según tu instancia)
NEO4J_URI=bolt://your-neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# PostgreSQL (configurar según tu instancia)
POSTGRES_HOST=your-postgres-host
POSTGRES_PORT=5432
POSTGRES_DB=your-database
POSTGRES_USER=your-user
POSTGRES_PASSWORD=your-password

# Sistema
ENV=production
LLM_ENABLED=true
PORT=8080
```

### Mejores Prácticas de Seguridad
1. **Secret Manager**: Usar Google Secret Manager para credenciales
2. **IAM**: Configurar roles mínimos necesarios
3. **VPC**: Conectar a bases de datos en VPC privada
4. **HTTPS**: Cloud Run incluye HTTPS automáticamente
5. **Autenticación**: Configurar IAM para endpoints sensibles

## 📊 Monitoreo y Logs

### Cloud Logging
```bash
# Ver logs del servicio
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=ida-microservice" --limit=50

# Logs en tiempo real
gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=ida-microservice"
```

### Métricas Importantes
- **Latencia de respuesta**: < 5 segundos para consultas típicas
- **Uso de memoria**: Monitor para optimizar asignación
- **Errores de agentes**: Fallos de conexión a bases de datos
- **Uso de Vertex AI**: Costos y límites de rate

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Error de Autenticación Vertex AI
```bash
# Verificar credenciales
gcloud auth application-default login
gcloud config set project prj-ia-tecnoandina
```

#### 2. Timeout en Cloud Run
```bash
# Aumentar timeout
gcloud run services update ida-microservice --timeout=600 --region=us-central1
```

#### 3. Error de Conexión a Bases de Datos
- Verificar configuraciones en variables de entorno
- Probar conexiones usando endpoints de test
- Verificar firewall y red

#### 4. Logs para Debug
```bash
# Logs detallados
gcloud run services logs read ida-microservice --region=us-central1 --limit=100
```

## 📈 Escalabilidad y Optimización

### Configuraciones de Producción
```bash
# Actualizar configuración de Cloud Run
gcloud run services update ida-microservice \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=50 \
  --min-instances=1 \
  --concurrency=100 \
  --region=us-central1
```

### Optimizaciones Recomendadas
1. **Connection Pooling**: Optimizar pools de conexión
2. **Caching**: Implementar Redis para consultas frecuentes
3. **Load Balancing**: Usar Cloud Load Balancer si es necesario
4. **Database Optimization**: Índices y query optimization
5. **Monitoring**: Cloud Monitoring y alertas

## ✅ Checklist de Despliegue

### Pre-despliegue
- [ ] Proyecto GCP configurado
- [ ] APIs habilitadas
- [ ] Credenciales configuradas
- [ ] Variables de entorno definidas
- [ ] Bases de datos accesibles

### Despliegue
- [ ] Imagen construida exitosamente
- [ ] Imagen subida a Container Registry
- [ ] Servicio desplegado en Cloud Run
- [ ] URL del servicio accesible
- [ ] Health check funcionando

### Post-despliegue
- [ ] Frontend carga correctamente
- [ ] Conexiones a bases de datos funcionan
- [ ] Consultas básicas responden
- [ ] Consultas complejas funcionan
- [ ] Logs sin errores críticos
- [ ] Monitoring configurado

## 🎯 Próximos Pasos

### Desarrollo Futuro
1. **Autenticación**: Implementar OAuth 2.0
2. **Rate Limiting**: Protección contra abuso
3. **Caching**: Redis para mejor rendimiento
4. **Monitoring**: Métricas personalizadas
5. **CI/CD**: Pipeline automatizado

### Integrations Potenciales
- **BigQuery**: Para análisis masivos
- **Cloud SQL**: Para PostgreSQL gestionado
- **Memorystore**: Para caching
- **Cloud Functions**: Para tareas async

---

## 📞 Soporte

Para problemas o consultas:
- **Email**: erbi.ramirez@tecnoandina.cl
- **Proyecto**: prj-ia-tecnoandina
- **Docs API**: https://[SERVICE-URL]/docs

---

**Última actualización**: 2025-06-04
**Versión**: 1.0.0
**Estado**: Producción Lista ✅
