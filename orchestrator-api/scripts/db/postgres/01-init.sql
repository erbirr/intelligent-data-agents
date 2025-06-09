-- =============================================================================
-- Script de inicialización unificado de PostgreSQL
-- Sistema Multi-Agente + Base de datos de Producción Agroindustrial
-- Base de datos: multiagentes
-- =============================================================================

-- PARTE 1: CONFIGURACIÓN INICIAL MULTI-AGENTE
-- =============================================================================

-- Crear esquemas principales para multi-agente
CREATE SCHEMA IF NOT EXISTS agents;
CREATE SCHEMA IF NOT EXISTS tasks;
CREATE SCHEMA IF NOT EXISTS workflows;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Crear esquemas para producción agroindustrial
CREATE SCHEMA IF NOT EXISTS produccion;
CREATE SCHEMA IF NOT EXISTS sensores;
CREATE SCHEMA IF NOT EXISTS control_calidad;

-- Crear usuario de aplicación con permisos específicos
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'tecnoandina') THEN
        CREATE ROLE tecnoandina WITH LOGIN PASSWORD 'tecnoandina';
    END IF;
END
$$;

-- Otorgar permisos en todos los esquemas
GRANT USAGE ON SCHEMA agents, tasks, workflows, monitoring, produccion, sensores, control_calidad TO tecnoandina;
GRANT CREATE ON SCHEMA agents, tasks, workflows, monitoring, produccion, sensores, control_calidad TO tecnoandina;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA agents, tasks, workflows, monitoring, produccion, sensores, control_calidad TO tecnoandina;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA agents, tasks, workflows, monitoring, produccion, sensores, control_calidad TO tecnoandina;

-- Crear extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- PARTE 2: SISTEMA DE PRODUCCIÓN AGROINDUSTRIAL
-- =============================================================================

-- Tabla de tipos de animales
CREATE TABLE produccion.tipos_animales (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    especie VARCHAR(50) NOT NULL,
    tiempo_crecimiento_dias INTEGER NOT NULL,
    peso_objetivo_kg DECIMAL(10,2),
    temperatura_optima_min DECIMAL(4,1),
    temperatura_optima_max DECIMAL(4,1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de granjas
CREATE TABLE produccion.granjas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(200),
    capacidad_maxima INTEGER,
    tipo_produccion VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de lotes de animales
CREATE TABLE produccion.lotes_animales (
    id SERIAL PRIMARY KEY,
    granja_id INTEGER REFERENCES produccion.granjas(id),
    tipo_animal_id INTEGER REFERENCES produccion.tipos_animales(id),
    cantidad_inicial INTEGER NOT NULL,
    cantidad_actual INTEGER NOT NULL,
    fecha_ingreso DATE NOT NULL,
    estado VARCHAR(20) DEFAULT 'activo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PARTE 3: SISTEMA MULTI-AGENTE
-- =============================================================================

-- Tabla de agentes
CREATE TABLE agents.agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'inactive',
    configuration JSONB,
    capabilities TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de tareas
CREATE TABLE tasks.tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents.agents(id),
    task_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Tabla de workflows
CREATE TABLE workflows.workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'created',
    configuration JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de pasos de workflow
CREATE TABLE workflows.workflow_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES workflows.workflows(id),
    step_order INTEGER NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    task_configuration JSONB,
    dependencies UUID[],
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PARTE 4: SISTEMA DE MONITOREO
-- =============================================================================

-- Tabla de métricas de agentes
CREATE TABLE monitoring.agent_metrics (
    id SERIAL PRIMARY KEY,
    agent_id UUID REFERENCES agents.agents(id),
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,4),
    metric_unit VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de logs del sistema
CREATE TABLE monitoring.system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    component VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PARTE 5: DATOS DE EJEMPLO
-- =============================================================================

-- Insertar tipos de animales
INSERT INTO produccion.tipos_animales (nombre, especie, tiempo_crecimiento_dias, peso_objetivo_kg, temperatura_optima_min, temperatura_optima_max) VALUES
('Cerdo Yorkshire', 'Sus scrofa', 180, 110.0, 18.0, 24.0),
('Pollo Broiler', 'Gallus gallus', 42, 2.5, 20.0, 24.0),
('Pavo Comercial', 'Meleagris gallopavo', 140, 8.0, 16.0, 21.0),
('Salmón Atlántico', 'Salmo salar', 730, 4.5, 8.0, 14.0);

-- Insertar granjas
INSERT INTO produccion.granjas (nombre, ubicacion, capacidad_maxima, tipo_produccion) VALUES
('Granja Norte', 'Región de Valparaíso', 5000, 'Porcino'),
('Granja Centro', 'Región Metropolitana', 10000, 'Avícola'),
('Granja Sur', 'Región del Biobío', 3000, 'Porcino'),
('Centro Acuícola Chiloé', 'Región de Los Lagos', 50000, 'Salmones');

-- Insertar lotes de ejemplo
INSERT INTO produccion.lotes_animales (granja_id, tipo_animal_id, cantidad_inicial, cantidad_actual, fecha_ingreso) VALUES
(1, 1, 500, 485, '2024-01-15'),
(2, 2, 8000, 7850, '2024-02-01'),
(3, 1, 300, 295, '2024-01-20'),
(4, 4, 25000, 24500, '2023-06-15');

-- Insertar agentes de ejemplo
INSERT INTO agents.agents (name, type, status, configuration, capabilities) VALUES
('Neo4j Agent', 'neo4j_agent', 'active', '{"uri": "bolt://localhost:7687", "database": "multiagentes"}', ARRAY['graph_queries', 'relationship_analysis']),
('PostgreSQL Agent', 'postgres_agent', 'active', '{"host": "localhost", "database": "multiagentes"}', ARRAY['sql_queries', 'data_analysis']),
('Orchestrator Agent', 'orchestrator', 'active', '{}', ARRAY['task_coordination', 'workflow_management']);

-- PARTE 6: ÍNDICES Y OPTIMIZACIONES
-- =============================================================================

-- Índices para mejor rendimiento
CREATE INDEX idx_agents_type_status ON agents.agents(type, status);
CREATE INDEX idx_tasks_agent_status ON tasks.tasks(agent_id, status);
CREATE INDEX idx_tasks_created_at ON tasks.tasks(created_at);
CREATE INDEX idx_workflow_steps_workflow_id ON workflows.workflow_steps(workflow_id, step_order);
CREATE INDEX idx_lotes_granja_tipo ON produccion.lotes_animales(granja_id, tipo_animal_id);
CREATE INDEX idx_agent_metrics_timestamp ON monitoring.agent_metrics(agent_id, timestamp);

-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar timestamps
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents.agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows.workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- PARTE 7: VISTAS ÚTILES
-- =============================================================================

-- Vista de resumen de agentes
CREATE VIEW monitoring.agents_summary AS
SELECT 
    a.type,
    a.status,
    COUNT(*) as count,
    MAX(a.updated_at) as last_activity
FROM agents.agents a
GROUP BY a.type, a.status;

-- Vista de producción actual
CREATE VIEW produccion.produccion_actual AS
SELECT 
    g.nombre as granja,
    ta.nombre as tipo_animal,
    SUM(la.cantidad_actual) as total_animales,
    AVG(CURRENT_DATE - la.fecha_ingreso) as dias_promedio_crecimiento
FROM produccion.lotes_animales la
JOIN produccion.granjas g ON la.granja_id = g.id
JOIN produccion.tipos_animales ta ON la.tipo_animal_id = ta.id
WHERE la.estado = 'activo'
GROUP BY g.nombre, ta.nombre;

-- Confirmación de inicialización
INSERT INTO monitoring.system_logs (level, component, message, metadata) 
VALUES ('INFO', 'database_init', 'Base de datos multiagentes inicializada correctamente', 
        jsonb_build_object('timestamp', CURRENT_TIMESTAMP, 'version', '1.0'));

-- Final del script
\echo 'Base de datos multiagentes inicializada correctamente'
