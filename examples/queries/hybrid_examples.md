# 🔄 Ejemplos de Consultas Híbridas

Este archivo contiene ejemplos de consultas que requieren datos de **ambas** bases de datos (Neo4j y PostgreSQL) y serán procesadas por el orquestador para combinar información inteligentemente.

## 🎯 **Palabras Clave que Activan Consultas Híbridas**

El orquestador detecta estas palabras y coordina ambos agentes:
- `combina`, `combine`, `correlaciona`, `correlate`
- `enriquece`, `enrich`, `mezcla`, `merge`
- `relaciona`, `relate`, `conecta con métricas`
- `híbrido`, `hybrid`, `multi-fuente`, `cross-database`
- `integra`, `integrate`, `fusiona`, `fuse`

## 🔄 **Ejemplos de Consultas Híbridas**

### **💼 Análisis de Clientes Enriquecido**

```text
"Combina las métricas de compra de clientes con sus relaciones sociales en el grafo"
```
**Proceso**:
1. **PostgreSQL**: Obtiene estadísticas de compra (total gastado, frecuencia, productos favoritos)
2. **Neo4j**: Analiza relaciones sociales y conexiones entre clientes
3. **Orquestador**: Combina ambos para perfiles enriquecidos

```text
"Correlaciona el valor de vida del cliente con su centralidad en la red social"
```
**Proceso**:
1. **PostgreSQL**: Calcula CLV (Customer Lifetime Value) por cliente
2. **Neo4j**: Calcula métricas de centralidad (betweenness, eigenvector)
3. **Orquestador**: Encuentra correlaciones entre ambas métricas

### **🛍️ Recomendaciones Inteligentes**

```text
"Recomienda productos basándote en historial de compras y conexiones de grafo"
```
**Proceso**:
1. **PostgreSQL**: Analiza patrones de compra históricos y preferencias
2. **Neo4j**: Identifica productos conectados y usuarios similares
3. **Orquestador**: Genera recomendaciones híbridas

```text
"Encuentra oportunidades de venta cruzada usando análisis relacional y de ventas"
```
**Proceso**:
1. **PostgreSQL**: Identifica productos frecuentemente comprados juntos
2. **Neo4j**: Analiza caminos de recomendación en el grafo
3. **Orquestador**: Combina ambos enfoques para mejores sugerencias

### **📊 Análisis de Segmentación Avanzada**

```text
"Segmenta clientes combinando comportamiento de compra y posición en la red"
```
**Proceso**:
1. **PostgreSQL**: Segmenta por RFM (Recency, Frequency, Monetary)
2. **Neo4j**: Clasifica por rol en la red (influencer, seguidor, hub)
3. **Orquestador**: Crea segmentos multidimensionales

```text
"Identifica comunidades de compradores con patrones similares de gasto"
```
**Proceso**:
1. **Neo4j**: Detecta comunidades en el grafo social
2. **PostgreSQL**: Analiza patrones de gasto por comunidad
3. **Orquestador**: Caracteriza cada comunidad con métricas financieras

### **🎯 Marketing y Campaña**

```text
"Optimiza campañas de marketing usando influencia de red y métricas de conversión"
```
**Proceso**:
1. **Neo4j**: Identifica usuarios influyentes y su alcance
2. **PostgreSQL**: Analiza tasas de conversión históricas
3. **Orquestador**: Selecciona targets óptimos para campañas

```text
"Mide el impacto viral de promociones combinando métricas de red y ventas"
```
**Proceso**:
1. **PostgreSQL**: Trackea incremento en ventas durante promociones
2. **Neo4j**: Analiza propagación de información en la red
3. **Orquestador**: Calcula coeficiente viral real

### **🕵️ Detección de Fraude y Anomalías**

```text
"Detecta fraudes combinando patrones transaccionales anómalos y redes sospechosas"
```
**Proceso**:
1. **PostgreSQL**: Identifica transacciones con patrones anómalos
2. **Neo4j**: Detecta redes de cuentas sospechosamente conectadas
3. **Orquestador**: Asigna scores de riesgo combinados

```text
"Identifica cuentas bot usando métricas de actividad y análisis de grafo"
```
**Proceso**:
1. **PostgreSQL**: Analiza patrones de actividad (frecuencia, timing)
2. **Neo4j**: Detecta patrones de conexión no naturales
3. **Orquestador**: Clasifica cuentas por probabilidad de ser bot

### **📈 Análisis de Crecimiento y Retención**

```text
"Analiza el crecimiento orgánico combinando métricas de usuario y propagación de red"
```
**Proceso**:
1. **PostgreSQL**: Trackea métricas de crecimiento (nuevos usuarios, retención)
2. **Neo4j**: Analiza cómo se propagan las invitaciones/referencias
3. **Orquestador**: Identifica drivers de crecimiento orgánico

```text
"Predice churn de clientes usando actividad transaccional y aislamiento social"
```
**Proceso**:
1. **PostgreSQL**: Analiza declive en actividad de compra
2. **Neo4j**: Detecta aislamiento progresivo en la red social
3. **Orquestador**: Genera predicciones de churn más precisas

### **🏪 Optimización de Inventario**

```text
"Optimiza inventario considerando demanda histórica y efectos de red de productos"
```
**Proceso**:
1. **PostgreSQL**: Analiza demanda histórica y estacionalidad
2. **Neo4j**: Modela cómo productos se influencian mutuamente en ventas
3. **Orquestador**: Genera recomendaciones de stock optimizadas

```text
"Identifica productos complementarios usando co-compras y análisis de grafo"
```
**Proceso**:
1. **PostgreSQL**: Analiza frecuencia de co-compras
2. **Neo4j**: Modela relaciones de complementariedad en grafo de productos
3. **Orquestador**: Ranquea pares de productos complementarios

## 🔧 **Consultas de Análisis Avanzado**

### **🧠 Business Intelligence Híbrido**

```text
"Genera un dashboard ejecutivo que combine KPIs financieros con métricas de red"
```
**Combina**:
- Métricas financieras (ingresos, márgenes, crecimiento)
- Métricas de red (engagement, viral coefficient, network health)

```text
"Analiza la salud del ecosistema combinando métricas operativas y de conectividad"
```
**Combina**:
- Métricas operativas (performance, eficiencia, costos)
- Métricas de red (densidad, centralización, componentes)

### **🔮 Análisis Predictivo Avanzado**

```text
"Predice tendencias de mercado usando análisis temporal y propagación de influencias"
```
**Combina**:
- Series temporales de ventas y actividad
- Modelos de difusión de información en redes

```text
"Modela el impacto de nuevos productos considerando canales de distribución y efectos de red"
```
**Combina**:
- Análisis de canales y performance histórica
- Simulación de adopción en redes sociales

### **⚖️ Análisis Comparativo Multidimensional**

```text
"Compara regiones no solo por métricas de venta sino por densidad y salud de redes locales"
```
**Combina**:
- Métricas regionales de venta y performance
- Análisis de redes sociales locales y conectividad

```text
"Benchmarka productos considerando performance financiero y posición en grafo de productos"
```
**Combina**:
- KPIs financieros por producto
- Métricas de centralidad en grafo de relaciones de productos

## 💡 **Casos de Uso Avanzados**

### **🎮 Gaming/Entretenimiento**

```text
"Optimiza engagement combinando métricas de juego con análisis de comunidades"
"Predice churn de jugadores usando actividad y aislamiento social"
"Identifica influencers para lanzamientos considerando reach y spending power"
```

### **🏢 B2B/Enterprise**

```text
"Analiza accounts considerando revenue potencial y posición en ecosystem de partners"
"Optimiza sales territories combinando métricas de pipeline con análisis de redes"
"Identifica key accounts usando influence mapping y transaction history"
```

### **🎓 EdTech/Educación**

```text
"Mejora retención estudiantil combinando performance académico con análisis de redes sociales"
"Optimiza formación de grupos considerando complementariedad de skills y compatibilidad social"
"Predice éxito de estudiantes usando historical data y social support network analysis"
```

## 🛠️ **Patrones de Implementación**

### **Sequential Pattern (Secuencial)**
```text
"Primero obtén métricas de venta por cliente, luego enriquece con análisis de influencia"
```
1. PostgreSQL → métricas base
2. Neo4j → enriquecimiento
3. Combinar resultados

### **Parallel Pattern (Paralelo)**
```text
"Simultáneamente analiza patrones de compra y detecta comunidades, luego correlaciona"
```
1. PostgreSQL || Neo4j → ejecución paralela
2. Merge inteligente de resultados

### **Iterative Pattern (Iterativo)**
```text
"Refina segmentación iterando entre análisis estadístico y de comunidades"
```
1. PostgreSQL → segmentación inicial
2. Neo4j → refinamiento por comunidades
3. Repetir hasta convergencia

## 🎯 **Tips para Consultas Híbridas Efectivas**

### **✅ Buenas Prácticas**
- **Sé específico** sobre qué quieres combinar
- **Usa palabras clave** de integración: "combina", "correlaciona", "enriquece"
- **Especifica el outcome** deseado: dashboard, predicción, optimización
- **Considera el contexto** de negocio para mejor interpretación

### **❌ Evitar**
- Consultas vagas que no especifican qué combinar
- Pedidos que no se benefician realmente de múltiples fuentes
- Consultas que podrían resolverse eficientemente con una sola fuente

---

**Nota**: Estas consultas híbridas requieren más tiempo de procesamiento pero proporcionan insights únicos que no serían posibles con una sola fuente de datos. El orquestador optimiza automáticamente el orden y paralelización de las consultas.
