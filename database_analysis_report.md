# REPORTE DE ANÁLISIS COMPLETO DE BASE DE DATOS

Fecha de generación: 2025-09-26 21:36:45

## RESUMEN EJECUTIVO

- **Total de registros**: 240,278
- **Total de tablas**: 3
- **Base de datos**: complete_analysis.duckdb

## DETALLE POR TABLA

### FACTURAS

- **Registros**: 78,210
- **Columnas**: 9
- **Estructura**:
  - `empresa_nit` (VARCHAR)
  - `empresa_ciudad` (VARCHAR)
  - `empresa_sede` (VARCHAR)
  - `empresa_nombre` (VARCHAR)
  - `fecha_hora` (VARCHAR)
  - `factura_num` (VARCHAR)
  - `ciente_numero` (BIGINT)
  - `pago_tipo` (VARCHAR)
  - `productos` (STRUCT(codigo VARCHAR, total INTEGER, valor_unitario INTEGER, descuento DOUBLE, IVA INTEGER)[])

### HISTORIAS_CLINICAS

- **Registros**: 85,815
- **Columnas**: 10
- **Estructura**:
  - `eps_nit` (VARCHAR)
  - `eps_nombre` (VARCHAR)
  - `historia_id` (BIGINT)
  - `paciente_cedula` (BIGINT)
  - `paciente_sexo` (VARCHAR)
  - `paciente_fecha_nacimiento` (VARCHAR)
  - `paciente_telefono` (VARCHAR)
  - `paciente_ciudad` (VARCHAR)
  - `fecha_ingreso_eps` (VARCHAR)
  - `listado_citas` (STRUCT(fecha_cita VARCHAR, peso_kg DOUBLE, altura_cm INTEGER, temperatura_c DOUBLE, mareo VARCHAR, dolor_corporal VARCHAR, examenes_laboratorio VARCHAR, medicamentos_post VARCHAR, requiere_tratamiento VARCHAR)[])

### TICKETES_VIAJES

- **Registros**: 76,253
- **Columnas**: 14
- **Estructura**:
  - `terminal_nit` (VARCHAR)
  - `terminal_nombre` (VARCHAR)
  - `ticket_id` (BIGINT)
  - `ticket_tipo` (VARCHAR)
  - `fecha_venta` (VARCHAR)
  - `empresa` (VARCHAR)
  - `vehiculo` (VARCHAR)
  - `puesto` (BIGINT)
  - `fecha_salida` (VARCHAR)
  - `cuidad_destino` (VARCHAR)
  - `cliente_identifica` (BIGINT)
  - `cliente_edad` (BIGINT)
  - `cliente_sexo` (VARCHAR)
  - `cliente_equipaje` (BIGINT)

## CONSULTAS DE EJEMPLO

```sql
-- Contar registros por tabla
SELECT COUNT(*) FROM facturas;
SELECT COUNT(*) FROM historias_clinicas;
SELECT COUNT(*) FROM ticketes_viajes;

-- Obtener muestra de datos
SELECT * FROM facturas LIMIT 5;
SELECT * FROM historias_clinicas LIMIT 5;
SELECT * FROM ticketes_viajes LIMIT 5;
```

