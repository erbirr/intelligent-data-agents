# 📡 API Endpoints Documentation

Esta documentación describe todos los endpoints disponibles en la API REST de Intelligent Data Agents.

## 🏠 **Base URLs**

| Environment | URL |
|-------------|-----|
| **Local Development** | `http://localhost:8080` |
| **Local Alternative** | `http://localhost:8081` |
| **Staging** | `https://intelligent-data-agents-staging-[hash].run.app` |
| **Production** | `https://intelligent-data-agents-[hash].run.app` |

## 🌐 **Root & Information**

### `GET /`
**Descripción**: Información básica de la API y enlaces principales.

**Response**:
```json
{
  "message": "MCP Microservice API",
  "docs": "/docs",
  "frontend": "/static/index.html"
}
```

### `GET /health`
**Descripción**: Health check del sistema y estado de agentes.

**Response**:
```json
{
  "status": "healthy",
  "service": "ida-microservice",
  "version": "1.0.0",
  "agents": {
    "neo4j": true,
    "postgres": true,
    "orchestrator": true
  }
}
```

### `GET /system/info`
**Descripción**: Información detallada del sistema y configuración.

**Response**:
```json
{
  "service": "MCP Microservice",
  "version": "1.0.0",
  "environment": "production",
  "cloud_project": "prj-ia-tecnoandina",
  "region": "us-central1",
  "llm_enabled": true,
  "endpoints": {
    "health": "/health",
    "query": "/query",
    "docs": "/docs",
    "frontend": "/static/index.html"
  }
}
```

## 🤖 **Agents Management**

### `GET /agents/status`
**Descripción**: Estado detallado de todos los agentes.

**Response**:
```json
{
  "neo4j": {
    "name": "neo4j_agent",
    "initialized": true,
    "connected": true,
    "resources_count": 4,
    "tools_count": 5,
    "connected_servers": [],
    "agent_type": "neo4j",
    "uri": "bolt://localhost:7687",
    "connection_details": {
      "uri": "bolt://localhost:7687",
      "user": "neo4j",
      "database_available": true
    }
  },
  "postgres": {
    "name": "postgres_agent",
    "initialized": true,
    "connected": true,
    "resources_count": 5,
    "tools_count": 7,
    "connected_servers": [],
    "agent_type": "postgresql",
    "host": "localhost",
    "database": "multiagentes",
    "connection_details": {
      "host": "localhost",
      "port": 5432,
      "database": "multiagentes",
      "user": "tecnoandina",
      "database_available": true,
      "pool_size": 10
    }
  },
  "orchestrator": {
    "name": "orchestrator",
    "initialized": true,
    "connected": true,
    "resources_count": 4,
    "tools_count": 5,
    "connected_servers": ["neo4j", "postgres"],
    "agent_type": "orchestrator",
    "agent_statuses": {
      "neo4j": {...},
      "postgres": {...}
    },
    "llm_status": {
      "connected": true,
      "stats": {...}
    }
  }
}
```

### `GET /agents/capabilities`
**Descripción**: Capacidades disponibles de cada agente.

**Response**:
```json
{
  "neo4j": [
    "graph_queries",
    "relationship_analysis", 
    "pattern_matching",
    "centrality_analysis",
    "community_detection"
  ],
  "postgres": [
    "sql_queries",
    "data_aggregation",
    "analytics",
    "time_series_analysis",
    "statistical_operations"
  ],
  "orchestrator": [
    "query_routing",
    "multi_agent_coordination",
    "result_synthesis",
    "llm_analysis",
    "hybrid_queries"
  ]
}
```

## 🔌 **Connection Testing**

### `POST /connections/neo4j/test`
**Descripción**: Prueba conexión a Neo4j con configuración personalizada.

**Request Body**:
```json
{
  "uri": "bolt://localhost:7687",
  "user": "neo4j",
  "password": "your_password",
  "database": "neo4j"
}
```

**Response Success**:
```json
{
  "success": true,
  "message": "Conexión exitosa a Neo4j",
  "details": {
    "name": "neo4j_agent",
    "initialized": true,
    "connected": true,
    "connection_details": {
      "uri": "bolt://localhost:7687",
      "user": "neo4j",
      "database_available": true
    }
  }
}
```

**Response Error**:
```json
{
  "success": false,
  "message": "Error conectando a Neo4j: Connection timeout"
}
```

### `POST /connections/postgres/test`
**Descripción**: Prueba conexión a PostgreSQL con configuración personalizada.

**Request Body**:
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "postgres",
  "user": "postgres",
  "password": "your_password"
}
```

**Response Success**:
```json
{
  "success": true,
  "message": "Conexión exitosa a PostgreSQL",
  "details": {
    "name": "postgres_agent",
    "initialized": true,
    "connected": true,
    "connection_details": {
      "host": "localhost",
      "port": 5432,
      "database": "postgres",
      "user": "postgres",
      "database_available": true,
      "pool_size": 10
    }
  }
}
```

## 🧠 **Intelligent Queries**

### `POST /query`
**Descripción**: Endpoint principal para consultas inteligentes en lenguaje natural.

**Request Body**:
```json
{
  "query": "¿Cuántos usuarios están conectados entre sí?",
  "context": {
    "type": "analysis",
    "priority": "high"
  },
  "neo4j_config": {
    "uri": "bolt://custom-neo4j:7687",
    "user": "neo4j",
    "password": "custom_password"
  },
  "postgres_config": {
    "host": "custom-postgres",
    "port": 5432,
    "database": "custom_db",
    "user": "custom_user",
    "password": "custom_password"
  }
}
```

**Response**:
```json
{
  "result": {
    "data": [
      {
        "total_users": 1250,
        "connected_users": 1100,
        "isolated_users": 150,
        "connectivity_rate": 0.88
      }
    ],
    "visualization": {
      "type": "graph",
      "nodes": 1250,
      "edges": 3400
    }
  },
  "metadata": {
    "query_type": "neo4j",
    "agent_used": "neo4j_agent",
    "processing_time": 2.3,
    "llm_analysis": {
      "confidence": 0.95,
      "keywords_detected": ["usuarios", "conectados"],
      "database_selected": "neo4j",
      "reasoning": "Query asks about user connections, which requires graph analysis"
    }
  },
  "execution_time": 2.8
}
```

#### **Query Types Examples**

**Neo4j Query**:
```json
{
  "query": "Muestra las relaciones entre productos más vendidos"
}
```

**PostgreSQL Query**:
```json
{
  "query": "Dame el promedio de ventas mensuales del último año"
}
```

**Hybrid Query**:
```json
{
  "query": "Combina las métricas de ventas con el análisis de relaciones entre clientes"
}
```

## 📊 **Response Formats**

### **Successful Response Structure**
```json
{
  "result": {
    "data": [...],           // Query results
    "visualization": {...},   // Visualization hints
    "summary": "..."         // Human-readable summary
  },
  "metadata": {
    "query_type": "string",        // neo4j, postgres, hybrid
    "agent_used": "string",        // Primary agent
    "agents_involved": [...],      // All agents used
    "processing_time": 0.0,        // Processing time in seconds
    "llm_analysis": {...},         // LLM reasoning
    "cache_hit": false             // Whether result was cached
  },
  "execution_time": 0.0            // Total execution time
}
```

### **Error Response Structure**
```json
{
  "detail": "Error message",
  "error_type": "validation_error | connection_error | processing_error",
  "error_code": "E001",
  "suggestions": [
    "Check your database connections",
    "Verify query syntax"
  ]
}
```

## 🎯 **Request Parameters**

### **Query Object**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | ✅ | Natural language query |
| `context` | object | ❌ | Additional context for query |
| `neo4j_config` | object | ❌ | Custom Neo4j connection |
| `postgres_config` | object | ❌ | Custom PostgreSQL connection |

### **Context Object**
| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Query type hint: analysis, report, dashboard |
| `priority` | string | Priority: low, normal, high |
| `user_id` | string | User identifier for logging |
| `session_id` | string | Session identifier |

### **Neo4j Config Object**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uri` | string | ✅ | Neo4j connection URI |
| `user` | string | ✅ | Username |
| `password` | string | ✅ | Password |
| `database` | string | ❌ | Database name (default: neo4j) |

### **PostgreSQL Config Object**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `host` | string | ✅ | PostgreSQL host |
| `port` | integer | ❌ | Port (default: 5432) |
| `database` | string | ✅ | Database name |
| `user` | string | ✅ | Username |
| `password` | string | ✅ | Password |

## 🔒 **Authentication**

Currently, the API is open for development. In production environments, consider implementing:

```http
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
```

## 📈 **Rate Limiting**

| Environment | Requests per minute |
|-------------|-------------------|
| Development | Unlimited |
| Staging | 100 rpm |
| Production | 1000 rpm |

## 🚨 **Error Codes**

| Code | Description |
|------|-------------|
| `E001` | Invalid query format |
| `E002` | Database connection failed |
| `E003` | LLM processing error |
| `E004` | Agent initialization failed |
| `E005` | Timeout error |
| `E006` | Rate limit exceeded |

## 📱 **Frontend Integration**

### **JavaScript Example**
```javascript
async function queryAgents(query) {
  const response = await fetch('/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      context: { type: 'analysis' }
    })
  });
  
  const result = await response.json();
  return result;
}
```

### **curl Example**
```bash
curl -X POST "http://localhost:8080/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuáles son los productos más conectados?",
    "context": {"type": "analysis"}
  }'
```

## 🔄 **WebSocket Support** (Future)

For real-time updates:
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // Handle real-time updates
};
```

---

**Documentation Version**: 1.0.0  
**Last Updated**: 2025-06-04  
**API Version**: 1.0.0
