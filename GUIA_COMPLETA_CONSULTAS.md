# GUÍA COMPLETA DE CONSULTAS Y ESTADÍSTICAS - BIG DATA ANALYTICS

## Universidad Central - Clase de Big Data y Analítica de Datos

---

## 📋 INTRODUCCIÓN

Esta guía proporciona un conjunto completo de consultas SQL y técnicas de análisis estadístico para el proyecto de Big Data Analytics. El sistema utiliza **DuckDB** como motor de base de datos analítica y contiene **240,278 registros** distribuidos en tres tablas principales.

## 🗄️ ESTRUCTURA DE LA BASE DE DATOS

### Tablas Disponibles

| Tabla | Registros | Descripción | Columnas Principales |
|-------|-----------|-------------|---------------------|
| `facturas` | 78,210 | Transacciones comerciales | id, empresa, fecha, monto, cliente |
| `historias_clinicas` | 85,815 | Registros médicos | id, eps, fecha, diagnostico, medico |
| `ticketes_viajes` | 76,253 | Boletos de transporte | id, empresa, origen, destino, precio |

---

## 🔍 CONSULTAS BÁSICAS DE EXPLORACIÓN

### 1. Información General de Tablas

```sql
-- Ver todas las tablas disponibles
SHOW TABLES;

-- Describir estructura de una tabla
DESCRIBE facturas;
DESCRIBE historias_clinicas;
DESCRIBE ticketes_viajes;

-- Conteo de registros por tabla
SELECT 'facturas' as tabla, COUNT(*) as registros FROM facturas
UNION ALL
SELECT 'historias_clinicas', COUNT(*) FROM historias_clinicas
UNION ALL
SELECT 'ticketes_viajes', COUNT(*) FROM ticketes_viajes;
```

### 2. Exploración de Datos

```sql
-- Muestra de primeros 10 registros
SELECT * FROM facturas LIMIT 10;
SELECT * FROM historias_clinicas LIMIT 10;
SELECT * FROM ticketes_viajes LIMIT 10;

-- Verificar calidad de datos (valores nulos)
SELECT 
    COUNT(*) as total_registros,
    COUNT(empresa) as empresa_no_nulos,
    COUNT(fecha) as fecha_no_nulos,
    COUNT(monto) as monto_no_nulos
FROM facturas;
```

---

## 📊 ANÁLISIS ESTADÍSTICO BÁSICO

### 1. Estadísticas Descriptivas - Facturas

```sql
-- Estadísticas básicas de montos
SELECT 
    COUNT(*) as total_facturas,
    MIN(CAST(monto AS DOUBLE)) as monto_minimo,
    MAX(CAST(monto AS DOUBLE)) as monto_maximo,
    ROUND(AVG(CAST(monto AS DOUBLE)), 2) as monto_promedio,
    ROUND(STDDEV(CAST(monto AS DOUBLE)), 2) as desviacion_estandar
FROM facturas 
WHERE monto IS NOT NULL;

-- Distribución por empresa
SELECT 
    empresa,
    COUNT(*) as total_facturas,
    ROUND(AVG(CAST(monto AS DOUBLE)), 2) as monto_promedio,
    ROUND(SUM(CAST(monto AS DOUBLE)), 2) as monto_total
FROM facturas 
WHERE empresa IS NOT NULL AND monto IS NOT NULL
GROUP BY empresa
ORDER BY total_facturas DESC;
```

### 2. Análisis Temporal - Facturas

```sql
-- Facturas por año y mes
SELECT 
    EXTRACT(YEAR FROM fecha) as año,
    EXTRACT(MONTH FROM fecha) as mes,
    COUNT(*) as total_facturas,
    ROUND(SUM(CAST(monto AS DOUBLE)), 2) as monto_total,
    ROUND(AVG(CAST(monto AS DOUBLE)), 2) as monto_promedio
FROM facturas 
WHERE fecha IS NOT NULL AND monto IS NOT NULL
GROUP BY EXTRACT(YEAR FROM fecha), EXTRACT(MONTH FROM fecha)
ORDER BY año DESC, mes DESC;

-- Tendencia mensual (últimos 12 meses)
SELECT 
    DATE_TRUNC('month', fecha) as mes,
    COUNT(*) as facturas,
    ROUND(SUM(CAST(monto AS DOUBLE)), 2) as facturacion_total
FROM facturas 
WHERE fecha >= '2023-01-01' AND monto IS NOT NULL
GROUP BY DATE_TRUNC('month', fecha)
ORDER BY mes DESC
LIMIT 12;
```

---

## 🏥 ANÁLISIS DE HISTORIAS CLÍNICAS

### 1. Diagnósticos Más Frecuentes

```sql
-- Top 20 diagnósticos más comunes
SELECT 
    diagnostico,
    COUNT(*) as frecuencia,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM historias_clinicas), 2) as porcentaje
FROM historias_clinicas
WHERE diagnostico IS NOT NULL
GROUP BY diagnostico
ORDER BY frecuencia DESC
LIMIT 20;

-- Distribución por EPS
SELECT 
    eps,
    COUNT(*) as total_historias,
    COUNT(DISTINCT diagnostico) as diagnosticos_unicos
FROM historias_clinicas
WHERE eps IS NOT NULL
GROUP BY eps
ORDER BY total_historias DESC;
```

### 2. Análisis de Médicos

```sql
-- Médicos más activos
SELECT 
    medico,
    COUNT(*) as total_consultas,
    COUNT(DISTINCT diagnostico) as diagnosticos_diferentes
FROM historias_clinicas
WHERE medico IS NOT NULL
GROUP BY medico
ORDER BY total_consultas DESC
LIMIT 15;

-- Especialización por médico (diagnóstico más frecuente)
SELECT 
    medico,
    diagnostico,
    COUNT(*) as frecuencia
FROM (
    SELECT 
        medico,
        diagnostico,
        COUNT(*) as frecuencia,
        ROW_NUMBER() OVER (PARTITION BY medico ORDER BY COUNT(*) DESC) as rn
    FROM historias_clinicas
    WHERE medico IS NOT NULL AND diagnostico IS NOT NULL
    GROUP BY medico, diagnostico
) t
WHERE rn = 1
ORDER BY frecuencia DESC
LIMIT 20;
```

---

## ✈️ ANÁLISIS DE TICKETS DE VIAJES

### 1. Destinos Más Populares

```sql
-- Top destinos por número de viajes
SELECT 
    destino,
    COUNT(*) as total_viajes,
    ROUND(AVG(CAST(precio AS DOUBLE)), 2) as precio_promedio,
    MIN(CAST(precio AS DOUBLE)) as precio_minimo,
    MAX(CAST(precio AS DOUBLE)) as precio_maximo
FROM ticketes_viajes
WHERE destino IS NOT NULL AND precio IS NOT NULL
GROUP BY destino
ORDER BY total_viajes DESC
LIMIT 15;

-- Rutas más transitadas (origen -> destino)
SELECT 
    origen,
    destino,
    COUNT(*) as viajes,
    ROUND(AVG(CAST(precio AS DOUBLE)), 2) as precio_promedio
FROM ticketes_viajes
WHERE origen IS NOT NULL AND destino IS NOT NULL AND precio IS NOT NULL
GROUP BY origen, destino
ORDER BY viajes DESC
LIMIT 20;
```

### 2. Análisis de Precios

```sql
-- Distribución de precios por empresa
SELECT 
    empresa,
    COUNT(*) as total_tickets,
    ROUND(MIN(CAST(precio AS DOUBLE)), 2) as precio_min,
    ROUND(MAX(CAST(precio AS DOUBLE)), 2) as precio_max,
    ROUND(AVG(CAST(precio AS DOUBLE)), 2) as precio_promedio,
    ROUND(STDDEV(CAST(precio AS DOUBLE)), 2) as desviacion_precio
FROM ticketes_viajes
WHERE empresa IS NOT NULL AND precio IS NOT NULL
GROUP BY empresa
ORDER BY precio_promedio DESC;
```

---

## 📊 ANÁLISIS AVANZADOS INTER-TABLAS

### 1. Análisis Comparativo de Volúmenes

```sql
-- Comparación de actividad por período
WITH monthly_activity AS (
    SELECT 
        'Facturas' as tipo,
        DATE_TRUNC('month', fecha) as mes,
        COUNT(*) as registros
    FROM facturas WHERE fecha IS NOT NULL
    GROUP BY DATE_TRUNC('month', fecha)
    
    UNION ALL
    
    SELECT 
        'Historias Clínicas',
        DATE_TRUNC('month', fecha),
        COUNT(*)
    FROM historias_clinicas WHERE fecha IS NOT NULL
    GROUP BY DATE_TRUNC('month', fecha)
    
    UNION ALL
    
    SELECT 
        'Tickets Viajes',
        DATE_TRUNC('month', fecha),
        COUNT(*)
    FROM ticketes_viajes WHERE fecha IS NOT NULL
    GROUP BY DATE_TRUNC('month', fecha)
)
SELECT 
    mes,
    SUM(CASE WHEN tipo = 'Facturas' THEN registros ELSE 0 END) as facturas,
    SUM(CASE WHEN tipo = 'Historias Clínicas' THEN registros ELSE 0 END) as historias,
    SUM(CASE WHEN tipo = 'Tickets Viajes' THEN registros ELSE 0 END) as tickets
FROM monthly_activity
GROUP BY mes
ORDER BY mes DESC
LIMIT 12;
```

### 2. Análisis de Calidad de Datos

```sql
-- Reporte de completitud por tabla
SELECT 
    'facturas' as tabla,
    COUNT(*) as total_registros,
    ROUND(COUNT(empresa) * 100.0 / COUNT(*), 2) as empresa_completitud,
    ROUND(COUNT(fecha) * 100.0 / COUNT(*), 2) as fecha_completitud,
    ROUND(COUNT(monto) * 100.0 / COUNT(*), 2) as monto_completitud
FROM facturas

UNION ALL

SELECT 
    'historias_clinicas',
    COUNT(*),
    ROUND(COUNT(eps) * 100.0 / COUNT(*), 2) as eps_completitud,
    ROUND(COUNT(fecha) * 100.0 / COUNT(*), 2) as fecha_completitud,
    ROUND(COUNT(diagnostico) * 100.0 / COUNT(*), 2) as diagnostico_completitud
FROM historias_clinicas

UNION ALL

SELECT 
    'ticketes_viajes',
    COUNT(*),
    ROUND(COUNT(empresa) * 100.0 / COUNT(*), 2) as empresa_completitud,
    ROUND(COUNT(origen) * 100.0 / COUNT(*), 2) as origen_completitud,
    ROUND(COUNT(destino) * 100.0 / COUNT(*), 2) as destino_completitud
FROM ticketes_viajes;
```

---

## 🎯 CONSULTAS DE BUSINESS INTELLIGENCE

### 1. KPIs Financieros (Facturas)

```sql
-- KPIs principales de facturación
SELECT 
    COUNT(*) as total_facturas,
    COUNT(DISTINCT empresa) as empresas_activas,
    ROUND(SUM(CAST(monto AS DOUBLE)), 2) as facturacion_total,
    ROUND(AVG(CAST(monto AS DOUBLE)), 2) as ticket_promedio,
    ROUND(STDDEV(CAST(monto AS DOUBLE)), 2) as volatilidad_ticket
FROM facturas 
WHERE monto IS NOT NULL;

-- Facturación por empresa (participación de mercado)
SELECT 
    empresa,
    COUNT(*) as facturas,
    ROUND(SUM(CAST(monto AS DOUBLE)), 2) as facturacion,
    ROUND(
        SUM(CAST(monto AS DOUBLE)) * 100.0 / 
        (SELECT SUM(CAST(monto AS DOUBLE)) FROM facturas WHERE monto IS NOT NULL), 
        2
    ) as participacion_mercado
FROM facturas 
WHERE empresa IS NOT NULL AND monto IS NOT NULL
GROUP BY empresa
ORDER BY facturacion DESC;
```

### 2. Métricas de Salud (Historias Clínicas)

```sql
-- Carga de trabajo por EPS
SELECT 
    eps,
    COUNT(*) as total_consultas,
    COUNT(DISTINCT medico) as medicos_activos,
    COUNT(DISTINCT diagnostico) as variedad_diagnosticos,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT medico), 2) as consultas_por_medico
FROM historias_clinicas
WHERE eps IS NOT NULL
GROUP BY eps
ORDER BY total_consultas DESC;
```

### 3. Métricas de Transporte (Tickets)

```sql
-- Eficiencia de rutas por empresa
SELECT 
    empresa,
    COUNT(*) as total_tickets,
    COUNT(DISTINCT CONCAT(origen, '-', destino)) as rutas_unicas,
    ROUND(AVG(CAST(precio AS DOUBLE)), 2) as precio_promedio,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT CONCAT(origen, '-', destino)), 2) as tickets_por_ruta
FROM ticketes_viajes
WHERE empresa IS NOT NULL AND origen IS NOT NULL AND destino IS NOT NULL
GROUP BY empresa
ORDER BY total_tickets DESC;
```

---

## 🔬 ANÁLISIS ESTADÍSTICOS AVANZADOS

### 1. Detección de Valores Atípicos

```sql
-- Outliers en facturas (usando método IQR)
WITH quartiles AS (
    SELECT 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY CAST(monto AS DOUBLE)) as q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY CAST(monto AS DOUBLE)) as q3
    FROM facturas 
    WHERE monto IS NOT NULL
),
iqr_bounds AS (
    SELECT 
        q1,
        q3,
        q3 - q1 as iqr,
        q1 - 1.5 * (q3 - q1) as lower_bound,
        q3 + 1.5 * (q3 - q1) as upper_bound
    FROM quartiles
)
SELECT 
    f.*,
    CAST(f.monto AS DOUBLE) as monto_numerico
FROM facturas f
CROSS JOIN iqr_bounds
WHERE CAST(f.monto AS DOUBLE) < lower_bound 
   OR CAST(f.monto AS DOUBLE) > upper_bound
ORDER BY CAST(f.monto AS DOUBLE) DESC;
```

### 2. Análisis de Correlaciones

```sql
-- Correlación entre volumen de facturas y montos promedio por empresa
WITH empresa_metrics AS (
    SELECT 
        empresa,
        COUNT(*) as volumen_facturas,
        ROUND(AVG(CAST(monto AS DOUBLE)), 2) as monto_promedio
    FROM facturas 
    WHERE empresa IS NOT NULL AND monto IS NOT NULL
    GROUP BY empresa
)
SELECT 
    CORR(volumen_facturas, monto_promedio) as correlacion_volumen_precio
FROM empresa_metrics;
```

---

## 💡 CONSULTAS PARA INSIGHTS DE NEGOCIO

### 1. Estacionalidad y Tendencias

```sql
-- Análisis de estacionalidad (facturas por día de la semana)
SELECT 
    EXTRACT(DOW FROM fecha) as dia_semana,
    CASE EXTRACT(DOW FROM fecha)
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END as nombre_dia,
    COUNT(*) as total_facturas,
    ROUND(AVG(CAST(monto AS DOUBLE)), 2) as monto_promedio
FROM facturas 
WHERE fecha IS NOT NULL AND monto IS NOT NULL
GROUP BY EXTRACT(DOW FROM fecha)
ORDER BY dia_semana;
```

### 2. Análisis de Concentración

```sql
-- Top 10% de clientes que generan el 80% de ingresos (Principio de Pareto)
WITH cliente_facturacion AS (
    SELECT 
        cliente,
        COUNT(*) as num_facturas,
        ROUND(SUM(CAST(monto AS DOUBLE)), 2) as facturacion_total
    FROM facturas 
    WHERE cliente IS NOT NULL AND monto IS NOT NULL
    GROUP BY cliente
),
cliente_ranking AS (
    SELECT 
        *,
        ROUND(
            facturacion_total * 100.0 / 
            (SELECT SUM(facturacion_total) FROM cliente_facturacion), 
            2
        ) as participacion,
        ROUND(
            SUM(facturacion_total) OVER (ORDER BY facturacion_total DESC) * 100.0 / 
            (SELECT SUM(facturacion_total) FROM cliente_facturacion), 
            2
        ) as participacion_acumulada
    FROM cliente_facturacion
)
SELECT 
    cliente,
    num_facturas,
    facturacion_total,
    participacion,
    participacion_acumulada
FROM cliente_ranking
WHERE participacion_acumulada <= 80
ORDER BY facturacion_total DESC;
```

---

## 🚀 CONSULTAS DE RENDIMIENTO OPTIMIZADAS

### 1. Índices Sugeridos para Mejorar Rendimiento

```sql
-- Crear índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_facturas_fecha ON facturas(fecha);
CREATE INDEX IF NOT EXISTS idx_facturas_empresa ON facturas(empresa);
CREATE INDEX IF NOT EXISTS idx_historias_eps ON historias_clinicas(eps);
CREATE INDEX IF NOT EXISTS idx_historias_diagnostico ON historias_clinicas(diagnostico);
CREATE INDEX IF NOT EXISTS idx_tickets_destino ON ticketes_viajes(destino);
CREATE INDEX IF NOT EXISTS idx_tickets_empresa ON ticketes_viajes(empresa);
```

### 2. Consultas con Ventanas Deslizantes

```sql
-- Análisis de tendencias con ventanas móviles (media móvil de 7 días)
SELECT 
    fecha,
    COUNT(*) as facturas_dia,
    ROUND(AVG(CAST(monto AS DOUBLE)), 2) as monto_promedio_dia,
    ROUND(
        AVG(COUNT(*)) OVER (
            ORDER BY fecha 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2
    ) as media_movil_7_dias
FROM facturas 
WHERE fecha IS NOT NULL AND monto IS NOT NULL
GROUP BY fecha
ORDER BY fecha DESC
LIMIT 30;
```

---

## 📈 REPORTES EJECUTIVOS

### 1. Dashboard de Métricas Clave

```sql
-- Resumen ejecutivo completo
SELECT 
    'Métricas Generales' as categoria,
    'Total de Registros' as metrica,
    (SELECT COUNT(*) FROM facturas) + 
    (SELECT COUNT(*) FROM historias_clinicas) + 
    (SELECT COUNT(*) FROM ticketes_viajes) as valor

UNION ALL

SELECT 
    'Facturas',
    'Facturación Total',
    ROUND(SUM(CAST(monto AS DOUBLE)), 0)
FROM facturas WHERE monto IS NOT NULL

UNION ALL

SELECT 
    'Historias Clínicas',
    'Diagnósticos Únicos',
    COUNT(DISTINCT diagnostico)
FROM historias_clinicas WHERE diagnostico IS NOT NULL

UNION ALL

SELECT 
    'Tickets Viajes',
    'Destinos Únicos',
    COUNT(DISTINCT destino)
FROM ticketes_viajes WHERE destino IS NOT NULL;
```

---

## 🛠️ HERRAMIENTAS DE MANTENIMIENTO

### 1. Verificación de Integridad de Datos

```sql
-- Verificar consistencia de datos
SELECT 
    'Facturas - Registros con monto cero' as verificacion,
    COUNT(*) as cantidad
FROM facturas 
WHERE CAST(monto AS DOUBLE) = 0

UNION ALL

SELECT 
    'Historias - Registros sin diagnóstico',
    COUNT(*)
FROM historias_clinicas 
WHERE diagnostico IS NULL OR TRIM(diagnostico) = ''

UNION ALL

SELECT 
    'Tickets - Origen = Destino',
    COUNT(*)
FROM ticketes_viajes 
WHERE origen = destino;
```

### 2. Estadísticas de Rendimiento de Consultas

```sql
-- Obtener estadísticas de la base de datos
SELECT 
    table_name,
    estimated_size as tamaño_estimado,
    column_count as numero_columnas
FROM duckdb_tables()
WHERE schema_name = 'main';
```

---

## 📚 NOTAS ADICIONALES

### Mejores Prácticas para Consultas

1. **Usar índices**: Siempre filtrar por columnas indexadas cuando sea posible
2. **Limitar resultados**: Usar `LIMIT` para consultas exploratorias
3. **Validar tipos**: Usar `CAST()` para conversiones de tipos explícitas
4. **Manejar nulos**: Siempre verificar valores NULL en condiciones WHERE
5. **Optimizar JOINs**: Usar índices en columnas de JOIN

### Función del Archivo

Este archivo sirve como:
- **Referencia rápida** para consultas comunes
- **Guía de aprendizaje** para técnicas de análisis SQL
- **Base de conocimiento** para insights de negocio
- **Herramienta de capacitación** para análisis de Big Data

---

**Desarrollado para**: Universidad Central - Clase de Big Data y Analítica de Datos  
**Tecnologías**: DuckDB, SQL, Python  
**Objetivo**: Demostrar competencias profesionales en análisis de datos masivos