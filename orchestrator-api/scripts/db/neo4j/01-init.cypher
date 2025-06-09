// =============================================================================
// Script de inicialización unificado de Neo4j
// Sistema Multi-Agente + Sistema de Producción Agroindustrial
// Base de datos: multiagentes
// =============================================================================

// PARTE 1: CREAR BASE DE DATOS MULTIAGENTES
// =============================================================================
CREATE DATABASE multiagentes IF NOT EXISTS;
:use multiagentes;

// PARTE 2: CONSTRAINTS E ÍNDICES DEL SISTEMA MULTI-AGENTE
// =============================================================================

// CONSTRAINTS DE UNICIDAD - MULTI-AGENTE
CREATE CONSTRAINT agent_unique_id IF NOT EXISTS 
    FOR (a:Agent) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT task_unique_id IF NOT EXISTS 
    FOR (t:Task) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT workflow_unique_id IF NOT EXISTS 
    FOR (w:Workflow) REQUIRE w.id IS UNIQUE;

// ÍNDICES REGULARES - MULTI-AGENTE
CREATE INDEX agent_status_index IF NOT EXISTS 
    FOR (a:Agent) ON (a.status);

CREATE INDEX task_status_index IF NOT EXISTS 
    FOR (t:Task) ON (t.status);

CREATE INDEX agent_type_index IF NOT EXISTS 
    FOR (a:Agent) ON (a.type);

CREATE INDEX task_priority_index IF NOT EXISTS 
    FOR (t:Task) ON (t.priority);

CREATE INDEX workflow_status_index IF NOT EXISTS 
    FOR (w:Workflow) ON (w.status);

// ÍNDICES COMPUESTOS - MULTI-AGENTE
CREATE INDEX agent_status_type_index IF NOT EXISTS 
    FOR (a:Agent) ON (a.status, a.type);

CREATE INDEX task_status_priority_index IF NOT EXISTS 
    FOR (t:Task) ON (t.status, t.priority);

// ÍNDICES TEMPORALES - MULTI-AGENTE
CREATE INDEX task_created_at_index IF NOT EXISTS 
    FOR (t:Task) ON (t.created_at);

CREATE INDEX workflow_created_at_index IF NOT EXISTS 
    FOR (w:Workflow) ON (w.created_at);

// PARTE 3: CONSTRAINTS PARA PRODUCCIÓN AGROINDUSTRIAL
// =============================================================================

// CONSTRAINTS DE UNICIDAD - PRODUCCIÓN
CREATE CONSTRAINT granja_unique_id IF NOT EXISTS 
    FOR (g:Granja) REQUIRE g.id IS UNIQUE;

CREATE CONSTRAINT animal_unique_id IF NOT EXISTS 
    FOR (a:Animal) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT lote_unique_id IF NOT EXISTS 
    FOR (l:Lote) REQUIRE l.id IS UNIQUE;

CREATE CONSTRAINT sensor_unique_id IF NOT EXISTS 
    FOR (s:Sensor) REQUIRE s.id IS UNIQUE;

// ÍNDICES REGULARES - PRODUCCIÓN
CREATE INDEX granja_tipo_index IF NOT EXISTS 
    FOR (g:Granja) ON (g.tipo_produccion);

CREATE INDEX animal_especie_index IF NOT EXISTS 
    FOR (a:Animal) ON (a.especie);

CREATE INDEX lote_estado_index IF NOT EXISTS 
    FOR (l:Lote) ON (l.estado);

CREATE INDEX sensor_tipo_index IF NOT EXISTS 
    FOR (s:Sensor) ON (s.tipo);

// ÍNDICES TEMPORALES - PRODUCCIÓN
CREATE INDEX lote_fecha_ingreso_index IF NOT EXISTS 
    FOR (l:Lote) ON (l.fecha_ingreso);

CREATE INDEX animal_fecha_nacimiento_index IF NOT EXISTS 
    FOR (a:Animal) ON (a.fecha_nacimiento);

// PARTE 4: DATOS INICIALES DEL SISTEMA MULTI-AGENTE
// =============================================================================

// Crear agentes principales
CREATE (neo4j_agent:Agent {
    id: "neo4j-agent-001",
    name: "Neo4j Agent",
    type: "neo4j_agent",
    status: "active",
    capabilities: ["graph_queries", "relationship_analysis", "pattern_detection"],
    configuration: {
        uri: "bolt://localhost:7687",
        database: "multiagentes",
        max_connections: 10
    },
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (postgres_agent:Agent {
    id: "postgres-agent-001",
    name: "PostgreSQL Agent",
    type: "postgres_agent", 
    status: "active",
    capabilities: ["sql_queries", "data_analysis", "reporting"],
    configuration: {
        host: "localhost",
        port: 5432,
        database: "multiagentes",
        max_connections: 20
    },
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (orchestrator_agent:Agent {
    id: "orchestrator-agent-001",
    name: "Orchestrator Agent",
    type: "orchestrator",
    status: "active", 
    capabilities: ["task_coordination", "workflow_management", "agent_communication"],
    configuration: {
        max_concurrent_tasks: 50,
        timeout_seconds: 300
    },
    created_at: datetime(),
    updated_at: datetime()
});

// Crear relaciones entre agentes
MATCH (o:Agent {type: "orchestrator"}), (n:Agent {type: "neo4j_agent"})
CREATE (o)-[:MANAGES]->(n);

MATCH (o:Agent {type: "orchestrator"}), (p:Agent {type: "postgres_agent"})
CREATE (o)-[:MANAGES]->(p);

MATCH (n:Agent {type: "neo4j_agent"}), (p:Agent {type: "postgres_agent"})
CREATE (n)-[:COLLABORATES_WITH]->(p);

// PARTE 5: DATOS DE PRODUCCIÓN AGROINDUSTRIAL
// =============================================================================

// Crear tipos de animales
CREATE (cerdo:TipoAnimal {
    id: "tipo-animal-001",
    nombre: "Cerdo Yorkshire",
    especie: "Sus scrofa",
    tiempo_crecimiento_dias: 180,
    peso_objetivo_kg: 110.0,
    temperatura_optima_min: 18.0,
    temperatura_optima_max: 24.0,
    created_at: datetime()
});

CREATE (pollo:TipoAnimal {
    id: "tipo-animal-002",
    nombre: "Pollo Broiler",
    especie: "Gallus gallus",
    tiempo_crecimiento_dias: 42,
    peso_objetivo_kg: 2.5,
    temperatura_optima_min: 20.0,
    temperatura_optima_max: 24.0,
    created_at: datetime()
});

CREATE (salmon:TipoAnimal {
    id: "tipo-animal-003",
    nombre: "Salmón Atlántico",
    especie: "Salmo salar",
    tiempo_crecimiento_dias: 730,
    peso_objetivo_kg: 4.5,
    temperatura_optima_min: 8.0,
    temperatura_optima_max: 14.0,
    created_at: datetime()
});

// Crear granjas
CREATE (granja_norte:Granja {
    id: "granja-001",
    nombre: "Granja Norte",
    ubicacion: "Región de Valparaíso",
    capacidad_maxima: 5000,
    tipo_produccion: "Porcino",
    coordenadas: {lat: -33.0458, lng: -71.6197},
    created_at: datetime()
});

CREATE (granja_centro:Granja {
    id: "granja-002",
    nombre: "Granja Centro", 
    ubicacion: "Región Metropolitana",
    capacidad_maxima: 10000,
    tipo_produccion: "Avícola",
    coordenadas: {lat: -33.4489, lng: -70.6693},
    created_at: datetime()
});

CREATE (centro_acuicola:Granja {
    id: "granja-003",
    nombre: "Centro Acuícola Chiloé",
    ubicacion: "Región de Los Lagos",
    capacidad_maxima: 50000,
    tipo_produccion: "Salmones",
    coordenadas: {lat: -42.6256, lng: -73.8161},
    created_at: datetime()
});

// Crear lotes de animales
CREATE (lote_001:Lote {
    id: "lote-001",
    cantidad_inicial: 500,
    cantidad_actual: 485,
    fecha_ingreso: date("2024-01-15"),
    estado: "activo",
    dias_crecimiento: duration.between(date("2024-01-15"), date()).days,
    created_at: datetime()
});

CREATE (lote_002:Lote {
    id: "lote-002",
    cantidad_inicial: 8000,
    cantidad_actual: 7850,
    fecha_ingreso: date("2024-02-01"),
    estado: "activo",
    dias_crecimiento: duration.between(date("2024-02-01"), date()).days,
    created_at: datetime()
});

CREATE (lote_003:Lote {
    id: "lote-003",
    cantidad_inicial: 25000,
    cantidad_actual: 24500,
    fecha_ingreso: date("2023-06-15"),
    estado: "activo",
    dias_crecimiento: duration.between(date("2023-06-15"), date()).days,
    created_at: datetime()
});

// Crear sensores
CREATE (sensor_temp_001:Sensor {
    id: "sensor-temp-001",
    tipo: "temperatura",
    modelo: "TempSense Pro",
    ubicacion: "Galpón A1",
    estado: "activo",
    valor_actual: 22.5,
    ultima_lectura: datetime(),
    created_at: datetime()
});

CREATE (sensor_hum_001:Sensor {
    id: "sensor-hum-001",
    tipo: "humedad",
    modelo: "HumidSense Pro",
    ubicacion: "Galpón A1", 
    estado: "activo",
    valor_actual: 65.0,
    ultima_lectura: datetime(),
    created_at: datetime()
});

// PARTE 6: RELACIONES DE PRODUCCIÓN
// =============================================================================

// Relaciones granja-tipo animal
MATCH (g:Granja {id: "granja-001"}), (t:TipoAnimal {id: "tipo-animal-001"})
CREATE (g)-[:CRIA]->(t);

MATCH (g:Granja {id: "granja-002"}), (t:TipoAnimal {id: "tipo-animal-002"})
CREATE (g)-[:CRIA]->(t);

MATCH (g:Granja {id: "granja-003"}), (t:TipoAnimal {id: "tipo-animal-003"})
CREATE (g)-[:CRIA]->(t);

// Relaciones granja-lote
MATCH (g:Granja {id: "granja-001"}), (l:Lote {id: "lote-001"})
CREATE (g)-[:CONTIENE]->(l);

MATCH (g:Granja {id: "granja-002"}), (l:Lote {id: "lote-002"})
CREATE (g)-[:CONTIENE]->(l);

MATCH (g:Granja {id: "granja-003"}), (l:Lote {id: "lote-003"})
CREATE (g)-[:CONTIENE]->(l);

// Relaciones lote-tipo animal
MATCH (l:Lote {id: "lote-001"}), (t:TipoAnimal {id: "tipo-animal-001"})
CREATE (l)-[:ES_DEL_TIPO]->(t);

MATCH (l:Lote {id: "lote-002"}), (t:TipoAnimal {id: "tipo-animal-002"})
CREATE (l)-[:ES_DEL_TIPO]->(t);

MATCH (l:Lote {id: "lote-003"}), (t:TipoAnimal {id: "tipo-animal-003"})
CREATE (l)-[:ES_DEL_TIPO]->(t);

// Relaciones granja-sensor
MATCH (g:Granja {id: "granja-001"}), (s:Sensor {id: "sensor-temp-001"})
CREATE (g)-[:TIENE_SENSOR]->(s);

MATCH (g:Granja {id: "granja-001"}), (s:Sensor {id: "sensor-hum-001"})
CREATE (g)-[:TIENE_SENSOR]->(s);

// PARTE 7: WORKFLOWS DE EJEMPLO
// =============================================================================

// Crear workflow de monitoreo
CREATE (workflow_monitoreo:Workflow {
    id: "workflow-001",
    name: "Monitoreo de Producción",
    description: "Workflow para monitorear la producción en tiempo real",
    status: "active",
    created_at: datetime(),
    updated_at: datetime()
});

// Crear tareas del workflow
CREATE (task_001:Task {
    id: "task-001",
    task_type: "sensor_reading",
    priority: 1,
    status: "pending",
    input_data: {sensor_ids: ["sensor-temp-001", "sensor-hum-001"]},
    created_at: datetime()
});

CREATE (task_002:Task {
    id: "task-002", 
    task_type: "data_analysis",
    priority: 2,
    status: "pending",
    input_data: {analysis_type: "temperature_trend"},
    created_at: datetime()
});

// Relaciones workflow-agent
MATCH (w:Workflow {id: "workflow-001"}), (a:Agent {type: "orchestrator"})
CREATE (w)-[:MANAGED_BY]->(a);

// Relaciones workflow-task
MATCH (w:Workflow {id: "workflow-001"}), (t:Task {id: "task-001"})
CREATE (w)-[:CONTAINS]->(t);

MATCH (w:Workflow {id: "workflow-001"}), (t:Task {id: "task-002"})
CREATE (w)-[:CONTAINS]->(t);

// Relaciones task-agent
MATCH (t:Task {id: "task-001"}), (a:Agent {type: "postgres_agent"})
CREATE (t)-[:ASSIGNED_TO]->(a);

MATCH (t:Task {id: "task-002"}), (a:Agent {type: "neo4j_agent"})
CREATE (t)-[:ASSIGNED_TO]->(a);

// PARTE 8: CONSULTAS DE VALIDACIÓN
// =============================================================================

// Verificar agentes creados
MATCH (a:Agent)
RETURN a.name, a.type, a.status;

// Verificar granjas y capacidad
MATCH (g:Granja)
RETURN g.nombre, g.tipo_produccion, g.capacidad_maxima;

// Verificar lotes activos
MATCH (g:Granja)-[:CONTIENE]->(l:Lote)-[:ES_DEL_TIPO]->(t:TipoAnimal)
WHERE l.estado = "activo"
RETURN g.nombre, t.nombre, l.cantidad_actual, l.dias_crecimiento;

// Verificar workflows activos
MATCH (w:Workflow)-[:CONTAINS]->(t:Task)-[:ASSIGNED_TO]->(a:Agent)
WHERE w.status = "active"
RETURN w.name, t.task_type, a.name;

// PARTE 9: FUNCIONES ÚTILES
// =============================================================================

// Crear procedimiento para obtener resumen de producción
CALL apoc.custom.asProcedure(
    'resumen.produccion',
    'MATCH (g:Granja)-[:CONTIENE]->(l:Lote)-[:ES_DEL_TIPO]->(t:TipoAnimal)
     WHERE l.estado = "activo"
     RETURN g.nombre as granja, 
            t.nombre as tipo_animal,
            sum(l.cantidad_actual) as total_animales,
            avg(l.dias_crecimiento) as dias_promedio
     ORDER BY total_animales DESC',
    'read',
    [['granja', 'string'], ['tipo_animal', 'string'], ['total_animales', 'int'], ['dias_promedio', 'float']]
);

// Crear función para calcular eficiencia de lote
CALL apoc.custom.asFunction(
    'lote.eficiencia',
    'RETURN toFloat($cantidad_actual) / $cantidad_inicial * 100',
    'float',
    [['cantidad_inicial', 'int'], ['cantidad_actual', 'int']]
);

// PARTE 10: CONFIGURACIÓN FINAL
// =============================================================================

// Crear nodo de configuración del sistema
CREATE (config:SystemConfig {
    id: "system-config-001",
    version: "1.0.0",
    initialized_at: datetime(),
    components: ["multi-agent", "production", "monitoring"],
    status: "active"
});

// Log de inicialización exitosa
CREATE (log:InitLog {
    id: "init-log-001",
    message: "Base de datos multiagentes Neo4j inicializada correctamente",
    timestamp: datetime(),
    version: "1.0.0",
    status: "success"
});

// Retornar confirmación
RETURN "Base de datos multiagentes Neo4j inicializada correctamente" as resultado;
