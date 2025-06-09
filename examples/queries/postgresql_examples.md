# 🗄️ Ejemplos de Consultas PostgreSQL

Este archivo contiene ejemplos de consultas que serán dirigidas automáticamente al agente PostgreSQL por el orquestador inteligente.

## 🎯 **Palabras Clave que Activan PostgreSQL**

El orquestador detecta estas palabras y dirige la consulta a PostgreSQL:
- `promedio`, `average`, `media`, `sum`, `suma`, `total`
- `contar`, `count`, `cantidad`, `número de`
- `máximo`, `max`, `mínimo`, `min`
- `grupo`, `group`, `agrupar`, `categoría`
- `fecha`, `time`, `temporal`, `mes`, `año`, `día`
- `tabla`, `table`, `registros`, `rows`, `filas`
- `estadísticas`, `stats`, `métricas`, `analytics`

## 📊 **Ejemplos de Consultas**

### **📈 Agregaciones y Estadísticas**

```text
"Dame el promedio de ventas por mes"
```
```text
"¿Cuál es el total de ingresos del último trimestre?"
```
```text
"Cuenta el número de usuarios registrados este año"
```
```text
"¿Cuál es el máximo valor de compra registrado?"
```

### **📅 Análisis Temporal**

```text
"Muestra las métricas de ventas de los últimos 6 meses"
```
```text
"¿Cómo han variado los ingresos año tras año?"
```
```text
"Dame el resumen mensual de transacciones de 2024"
```
```text
"¿Cuál ha sido el mes con mayor actividad?"
```

### **👥 Análisis por Categorías**

```text
"Agrupa las ventas por categoría de producto"
```
```text
"¿Cuántos usuarios hay por región geográfica?"
```
```text
"Dame las estadísticas de compra por grupo de edad"
```
```text
"Analiza el rendimiento por canal de venta"
```

### **💰 Análisis Financiero**

```text
"Calcula el ingreso total por producto"
```
```text
"¿Cuál es el margen de ganancia promedio?"
```
```text
"Dame el top 10 de productos más rentables"
```
```text
"Analiza la evolución de costos operativos"
```

### **📊 Rankings y Top Lists**

```text
"¿Cuáles son los 5 productos más vendidos?"
```
```text
"Dame el ranking de clientes por volumen de compra"
```
```text
"Top 10 de regiones con mayor crecimiento"
```
```text
"¿Quiénes son los vendedores más exitosos?"
```

### **🔍 Análisis de Segmentación**

```text
"Segmenta clientes por frecuencia de compra"
```
```text
"¿Cómo se distribuyen las ventas por rango de precios?"
```
```text
"Analiza el comportamiento de compra por demografía"
```
```text
"Clasifica productos por performance de ventas"
```

### **📉 Análisis de Tendencias**

```text
"¿Hay tendencias estacionales en las ventas?"
```
```text
"Analiza el crecimiento mes a mes"
```
```text
"¿Qué productos muestran declive en ventas?"
```
```text
"Identifica patrones de crecimiento por categoría"
```

### **⚖️ Comparativas**

```text
"Compara el rendimiento de este año vs el anterior"
```
```text
"¿Cómo se comparan las ventas online vs tienda física?"
```
```text
"Contrasta el performance por región"
```
```text
"Compara la efectividad de diferentes campañas"
```

## 🔧 **Consultas Técnicas**

### **📋 Exploración de Datos**

```text
"¿Cuántas tablas hay en la base de datos?"
```
```text
"Dame un resumen de la estructura de datos"
```
```text
"¿Qué columnas tiene la tabla de ventas?"
```
```text
"Muestra las primeras 10 filas de productos"
```

### **🧮 Cálculos Complejos**

```text
"Calcula la tasa de conversión por canal"
```
```text
"¿Cuál es el valor de vida del cliente promedio?"
```
```text
"Computa el ROI de campañas de marketing"
```
```text
"Calcula la rotación de inventario por producto"
```

### **📊 Métricas de Negocio**

```text
"¿Cuál es la tasa de retención de clientes?"
```
```text
"Calcula el tiempo promedio entre compras"
```
```text
"¿Cuál es el ticket promedio por transacción?"
```
```text
"Dame las métricas de abandono de carrito"
```

### **🔍 Análisis de Calidad de Datos**

```text
"¿Hay registros duplicados en la tabla de clientes?"
```
```text
"Identifica valores nulos en datos críticos"
```
```text
"¿Qué porcentaje de datos está completo?"
```
```text
"Verifica la consistencia de formatos de fecha"
```

## 💡 **Consultas Avanzadas**

### **🎯 Business Intelligence**

```text
"Dame un dashboard completo de KPIs de ventas"
```
```text
"Genera un reporte ejecutivo del último trimestre"
```
```text
"¿Cuáles son las métricas clave de performance?"
```
```text
"Analiza la salud financiera del negocio"
```

### **🔮 Análisis Predictivo Básico**

```text
"¿Cuál es la proyección de ventas basada en históricos?"
```
```text
"Identifica productos con riesgo de obsolescencia"
```
```text
"¿Qué clientes tienen mayor probabilidad de churn?"
```
```text
"Predice la demanda del próximo mes"
```

### **⚡ Análisis de Performance**

```text
"¿Cuáles son las consultas más lentas del sistema?"
```
```text
"Analiza el uso de espacio por tabla"
```
```text
"¿Qué índices necesitan optimización?"
```
```text
"Dame estadísticas de performance de la base"
```

## 🎯 **Casos de Uso por Industria**

### **🛒 E-commerce**
```text
"Analiza el embudo de conversión de ventas"
"¿Cuál es el valor promedio del carrito de compras?"
"Dame las métricas de abandono por etapa"
"Analiza la efectividad de descuentos y promociones"
```

### **🏦 Finanzas**
```text
"Calcula el riesgo crediticio promedio por segmento"
"¿Cuál es la morosidad por tipo de préstamo?"
"Analiza la rentabilidad por producto financiero"
"Dame las métricas de liquidez y solvencia"
```

### **🏥 Salud**
```text
"¿Cuál es el tiempo promedio de tratamiento?"
"Analiza la ocupación de camas por departamento"
"Dame estadísticas de readmisiones hospitalarias"
"Calcula la eficiencia operativa por servicio"
```

### **🎓 Educación**
```text
"¿Cuál es la tasa de graduación por programa?"
"Analiza el rendimiento académico por curso"
"Dame las estadísticas de deserción estudiantil"
"Calcula el ratio profesor-estudiante por facultad"
```

## 💡 **Tips para Mejores Consultas**

### **✅ Buenas Prácticas**
- Usa términos cuantitativos: "promedio", "total", "máximo"
- Especifica períodos de tiempo: "último mes", "este año"
- Incluye agrupaciones: "por categoría", "por región"
- Menciona métricas específicas: "KPIs", "estadísticas"

### **❌ Evitar**
- Términos exclusivos de grafos: "nodos", "aristas", "conexiones"
- Consultas sobre relaciones complejas (mejor para Neo4j)
- Análisis de redes sociales o patrones de grafo

## 🔗 **Integración con Neo4j**

Algunas consultas pueden beneficiarse de datos de ambas fuentes:
```text
"Combina las métricas de ventas con el análisis de relaciones de clientes"
"Enriquece el análisis financiero con datos de conectividad de productos"
"Correlaciona las estadísticas de uso con los patrones de red social"
```

---

**Nota**: Todas estas consultas serán procesadas automáticamente por el orquestador y dirigidas al agente PostgreSQL. Los resultados incluirán tablas, gráficos y métricas cuando sea apropiado.
