# 🔗 Ejemplos de Consultas Neo4j

Este archivo contiene ejemplos de consultas que serán dirigidas automáticamente al agente Neo4j por el orquestador inteligente.

## 🎯 **Palabras Clave que Activan Neo4j**

El orquestador detecta estas palabras y dirige la consulta a Neo4j:
- `relaciones`, `relationships`, `conectado`, `connected`
- `grafo`, `graph`, `nodos`, `nodes`, `aristas`, `edges`
- `camino`, `path`, `ruta`, `route`
- `central`, `centrality`, `influencia`, `influence`
- `comunidad`, `community`, `cluster`
- `vecinos`, `neighbors`, `adyacente`, `adjacent`

## 📊 **Ejemplos de Consultas**

### **🔍 Análisis de Relaciones**

```text
"¿Qué productos están más conectados entre sí?"
```
```text
"Muestra las relaciones entre usuarios y productos"
```
```text
"¿Cómo están conectados los clientes con las categorías de productos?"
```

### **🗺️ Análisis de Caminos**

```text
"Encuentra el camino más corto entre dos usuarios"
```
```text
"¿Cuál es la ruta de recomendación más efectiva para este producto?"
```
```text
"Muestra todos los caminos entre el usuario A y el producto B"
```

### **⭐ Análisis de Centralidad**

```text
"¿Cuáles son los nodos más influyentes en la red?"
```
```text
"Identifica los usuarios más centrales en el grafo de interacciones"
```
```text
"¿Qué productos tienen mayor centralidad de intermediación?"
```

### **👥 Análisis de Comunidades**

```text
"Detecta comunidades de usuarios con intereses similares"
```
```text
"Agrupa productos en clusters según sus relaciones"
```
```text
"¿Qué comunidades de compradores existen en los datos?"
```

### **🔍 Análisis de Vecindario**

```text
"¿Cuáles son los vecinos directos de este usuario?"
```
```text
"Muestra todos los productos adyacentes a esta categoría"
```
```text
"¿Qué usuarios están a 2 saltos de distancia?"
```

### **📈 Análisis de Patrones**

```text
"Detecta patrones anómalos en las conexiones"
```
```text
"¿Hay ciclos en las relaciones de recomendación?"
```
```text
"Identifica triángulos en el grafo de usuarios"
```

### **🎯 Recomendaciones Basadas en Grafo**

```text
"Recomienda productos basándote en el análisis de relaciones"
```
```text
"¿Qué usuarios podrían estar interesados en este producto según el grafo?"
```
```text
"Encuentra productos similares usando análisis de vecindario"
```

### **📊 Métricas de Grafo**

```text
"¿Cuál es el grado promedio de los nodos en el grafo?"
```
```text
"Calcula la densidad de la red de relaciones"
```
```text
"¿Cuál es el diámetro del grafo de usuarios?"
```

## 🔧 **Consultas Técnicas**

### **Exploración de Estructura**

```text
"¿Cuántos nodos y aristas tiene el grafo?"
```
```text
"Lista todas las etiquetas de nodos disponibles"
```
```text
"¿Qué tipos de relaciones existen en el grafo?"
```

### **Análisis de Conectividad**

```text
"¿El grafo está conectado o tiene componentes separados?"
```
```text
"Identifica componentes aislados en la red"
```
```text
"¿Hay nodos huérfanos sin conexiones?"
```

### **Análisis Temporal (si hay timestamps)**

```text
"¿Cómo han evolucionado las conexiones en el tiempo?"
```
```text
"Muestra el grafo de relaciones del último mes"
```
```text
"¿Qué conexiones son más recientes?"
```

## 💡 **Tips para Mejores Consultas**

### **✅ Buenas Prácticas**
- Usa términos específicos de grafos: "nodos", "aristas", "conexiones"
- Sé específico sobre el tipo de análisis: "centralidad", "comunidades", "caminos"
- Incluye contexto: "en el grafo de usuarios", "entre productos"

### **❌ Evitar**
- Consultas muy genéricas sin contexto de grafo
- Términos exclusivamente de bases relacionales: "tabla", "fila", "columna"
- Agregaciones numéricas simples (mejor para PostgreSQL)

## 🎯 **Casos de Uso Comunes**

### **E-commerce**
```text
"¿Qué productos compran juntos los usuarios conectados?"
"Identifica influencers en la red de compradores"
"Detecta comunidades de compradores por categoría"
```

### **Redes Sociales**
```text
"¿Quiénes son los usuarios más influyentes?"
"Detecta comunidades de usuarios con intereses similares"
"Encuentra el camino de conexión entre dos usuarios"
```

### **Logística**
```text
"¿Cuál es la ruta más eficiente entre almacenes?"
"Identifica cuellos de botella en la red de distribución"
"Analiza la conectividad de centros logísticos"
```

### **Fraude/Seguridad**
```text
"Detecta patrones anómalos en las transacciones conectadas"
"¿Hay redes de cuentas sospechosas conectadas?"
"Identifica clusters de actividad fraudulenta"
```

---

**Nota**: Todas estas consultas serán procesadas automáticamente por el orquestador y dirigidas al agente Neo4j. Los resultados incluirán visualizaciones de nodos y relaciones cuando sea apropiado.
