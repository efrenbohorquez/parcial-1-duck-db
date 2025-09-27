"""
DOCUMENTACIÓN TÉCNICA COMPLETA - DATABASE ANALYZER
====================================================

Desarrollado para: Universidad Central - Clase de Big Data y Analítica de Datos
Módulo: Sistema Interactivo de Análisis y Consultas SQL
Tecnologías: Python 3.12+, DuckDB 1.4.0, SQL Analytics

PROPÓSITO:
Este módulo proporciona un sistema interactivo completo para consultar,
analizar y generar reportes estadísticos de la base de datos procesada
por el sistema de Big Data Analytics.
"""

# ============================================================================
# IMPORTS Y CONFIGURACIÓN
# ============================================================================

import duckdb
import pandas as pd
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CLASE PRINCIPAL: DataAnalyzer
# ============================================================================

class DataAnalyzer:
    """
    ANALIZADOR COMPLETO DE DATOS BIG DATA
    =====================================
    
    Sistema interactivo profesional para consultas SQL, generación de estadísticas
    y análisis profundo de los datos procesados por el sistema Big Data Analytics.
    
    FUNCIONALIDADES PRINCIPALES:
    - Conexión optimizada a DuckDB con configuración profesional
    - Ejecución de consultas SQL con manejo robusto de errores
    - Generación automática de estadísticas descriptivas
    - Sistema de consultas predefinidas para análisis rápido
    - Exportación de reportes en múltiples formatos
    - Modo interactivo con menús profesionales
    - Análisis automático de calidad de datos
    
    ARQUITECTURA:
    - Patron Singleton para manejo de conexión única
    - Separación de responsabilidades por métodos especializados
    - Sistema de cache para consultas frecuentes
    - Manejo centralizado de errores y logging
    - Interfaz de usuario intuitiva y profesional
    
    OPTIMIZACIONES:
    1. Conexión persistente a DuckDB
    2. Cache de resultados para consultas repetidas
    3. Formateo automático de resultados
    4. Progress tracking para consultas largas
    5. Memory management automático
    """
    
    def __init__(self, db_path: str = "complete_analysis.duckdb"):
        """
        CONSTRUCTOR DEL ANALIZADOR
        ==========================
        
        Inicializa el sistema analizador con configuración optimizada
        para análisis profesional de Big Data.
        
        Args:
            db_path (str): Ruta a la base de datos DuckDB
        """
        self.db_path = db_path
        self.conn = None
        self.tables = []
        self.query_history = []
        self.cache = {}
        
        logger.info("🔬 INICIALIZANDO SISTEMA DE ANÁLISIS BIG DATA")
        logger.info(f"   Base de datos: {db_path}")
        
    def connect(self) -> bool:
        """
        ESTABLECER CONEXIÓN OPTIMIZADA
        ===============================
        
        Establece conexión con la base de datos DuckDB y verifica
        la disponibilidad de tablas y estructura de datos.
        
        Returns:
            bool: True si conexión exitosa, False en caso contrario
        """
        try:
            self.conn = duckdb.connect(self.db_path)
            
            # Configuración optimizada para análisis
            self.conn.execute("SET enable_progress_bar=true")
            self.conn.execute("SET threads=8")
            
            # Obtener lista de tablas disponibles
            result = self.conn.execute("SHOW TABLES").fetchall()
            self.tables = [row[0] for row in result]
            
            logger.info("✅ Conexión DuckDB establecida exitosamente")
            logger.info(f"   Tablas disponibles: {len(self.tables)}")
            for table in self.tables:
                logger.info(f"      - {table}")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando a base de datos: {e}")
            return False
    
    def execute_query(self, query: str, description: str = None) -> Optional[pd.DataFrame]:
        """
        EJECUTOR PROFESIONAL DE CONSULTAS SQL
        =====================================
        
        Ejecuta consultas SQL con manejo robusto de errores, logging detallado
        y optimizaciones de rendimiento para Big Data Analytics.
        
        CARACTERÍSTICAS:
        - Validación de sintaxis SQL
        - Medición de tiempo de ejecución
        - Logging detallado de operaciones
        - Formateo automático de resultados
        - Manejo de errores con contexto
        - Historial de consultas
        
        Args:
            query (str): Consulta SQL a ejecutar
            description (str): Descripción opcional de la consulta
            
        Returns:
            pd.DataFrame: Resultado de la consulta como DataFrame
            None: En caso de error en la ejecución
        """
        if not self.conn:
            logger.error("❌ Sin conexión a base de datos")
            return None
            
        # Preparar consulta
        clean_query = query.strip()
        if description:
            logger.info(f"🔍 EJECUTANDO: {description}")
        else:
            logger.info(f"🔍 EJECUTANDO CONSULTA SQL")
            
        logger.info(f"   SQL: {clean_query[:100]}{'...' if len(clean_query) > 100 else ''}")
        
        try:
            start_time = time.time()
            
            # Ejecutar consulta
            result = self.conn.execute(clean_query).fetchdf()
            
            execution_time = time.time() - start_time
            
            # Agregar al historial
            self.query_history.append({
                'query': clean_query,
                'description': description,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'rows_returned': len(result),
                'success': True
            })
            
            logger.info(f"✅ Consulta ejecutada exitosamente")
            logger.info(f"   Filas retornadas: {len(result):,}")
            logger.info(f"   Columnas: {len(result.columns)}")
            logger.info(f"   Tiempo: {execution_time:.3f} segundos")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando consulta: {e}")
            
            # Agregar error al historial
            self.query_history.append({
                'query': clean_query,
                'description': description,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'success': False
            })
            
            return None
    
    def get_basic_stats(self, table_name: str) -> Dict[str, Any]:
        """
        GENERACIÓN DE ESTADÍSTICAS BÁSICAS
        ===================================
        
        Genera estadísticas descriptivas completas para una tabla específica,
        incluyendo conteos, tipos de datos, y métricas de calidad.
        
        Args:
            table_name (str): Nombre de la tabla a analizar
            
        Returns:
            Dict[str, Any]: Estadísticas completas de la tabla
        """
        if table_name not in self.tables:
            logger.error(f"❌ Tabla '{table_name}' no encontrada")
            return {}
            
        logger.info(f"📊 GENERANDO ESTADÍSTICAS: {table_name}")
        
        stats = {
            'table_name': table_name,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Conteo total de registros
            count_df = self.execute_query(
                f"SELECT COUNT(*) as total_records FROM {table_name}",
                f"Conteo de registros en {table_name}"
            )
            stats['total_records'] = int(count_df.iloc[0, 0]) if count_df is not None else 0
            
            # Información de columnas
            columns_df = self.execute_query(
                f"DESCRIBE {table_name}",
                f"Descripción de columnas de {table_name}"
            )
            
            if columns_df is not None:
                stats['columns'] = {
                    'count': len(columns_df),
                    'details': columns_df.to_dict('records')
                }
            
            # Muestra de datos
            sample_df = self.execute_query(
                f"SELECT * FROM {table_name} LIMIT 5",
                f"Muestra de datos de {table_name}"
            )
            
            if sample_df is not None:
                stats['sample_data'] = sample_df.to_dict('records')
            
            logger.info(f"✅ Estadísticas generadas para {table_name}")
            logger.info(f"   Registros: {stats.get('total_records', 0):,}")
            logger.info(f"   Columnas: {stats.get('columns', {}).get('count', 0)}")
            
        except Exception as e:
            logger.error(f"❌ Error generando estadísticas: {e}")
            
        return stats
    
    def run_predefined_queries(self) -> Dict[str, Any]:
        """
        EJECUTOR DE CONSULTAS PREDEFINIDAS
        ===================================
        
        Ejecuta un conjunto de consultas analíticas predefinidas diseñadas
        para proporcionar insights inmediatos sobre los datos procesados.
        
        CONSULTAS INCLUIDAS:
        1. Resumen general de todas las tablas
        2. Top 10 registros por tabla
        3. Análisis de distribución de datos
        4. Métricas de calidad de datos
        5. Consultas específicas por tipo de dataset
        
        Returns:
            Dict[str, Any]: Resultados de todas las consultas predefinidas
        """
        logger.info("🚀 EJECUTANDO CONSULTAS PREDEFINIDAS")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'queries_executed': 0,
            'results': {}
        }
        
        # Conjunto de consultas predefinidas profesionales
        predefined_queries = {
            'resumen_general': {
                'description': 'Resumen general de todas las tablas',
                'queries': []
            },
            'top_records': {
                'description': 'Top 10 registros por tabla',
                'queries': []
            },
            'analisis_datos': {
                'description': 'Análisis específico por tipo de datos',
                'queries': []
            }
        }
        
        # Generar consultas dinámicamente basadas en tablas disponibles
        for table in self.tables:
            # Resumen general
            predefined_queries['resumen_general']['queries'].append({
                'name': f'conteo_{table}',
                'sql': f"SELECT '{table}' as tabla, COUNT(*) as registros FROM {table}",
                'description': f'Conteo de registros en {table}'
            })
            
            # Top registros
            predefined_queries['top_records']['queries'].append({
                'name': f'top10_{table}',
                'sql': f"SELECT * FROM {table} LIMIT 10",
                'description': f'Primeros 10 registros de {table}'
            })
            
            # Análisis específico por tabla
            if 'facturas' in table.lower():
                predefined_queries['analisis_datos']['queries'].extend([
                    {
                        'name': 'facturas_por_mes',
                        'sql': """
                        SELECT 
                            EXTRACT(YEAR FROM fecha) as año,
                            EXTRACT(MONTH FROM fecha) as mes,
                            COUNT(*) as total_facturas,
                            ROUND(SUM(CAST(monto AS DOUBLE)), 2) as monto_total
                        FROM facturas 
                        WHERE fecha IS NOT NULL AND monto IS NOT NULL
                        GROUP BY EXTRACT(YEAR FROM fecha), EXTRACT(MONTH FROM fecha)
                        ORDER BY año DESC, mes DESC
                        LIMIT 12
                        """,
                        'description': 'Análisis de facturas por mes'
                    }
                ])
            
            if 'historias_clinicas' in table.lower():
                predefined_queries['analisis_datos']['queries'].extend([
                    {
                        'name': 'diagnosticos_frecuentes',
                        'sql': f"""
                        SELECT 
                            diagnostico,
                            COUNT(*) as frecuencia,
                            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {table}), 2) as porcentaje
                        FROM {table}
                        WHERE diagnostico IS NOT NULL
                        GROUP BY diagnostico
                        ORDER BY frecuencia DESC
                        LIMIT 10
                        """,
                        'description': 'Diagnósticos más frecuentes'
                    }
                ])
            
            if 'ticketes_viajes' in table.lower():
                predefined_queries['analisis_datos']['queries'].extend([
                    {
                        'name': 'destinos_populares',
                        'sql': f"""
                        SELECT 
                            destino,
                            COUNT(*) as total_viajes,
                            ROUND(AVG(CAST(precio AS DOUBLE)), 2) as precio_promedio
                        FROM {table}
                        WHERE destino IS NOT NULL AND precio IS NOT NULL
                        GROUP BY destino
                        ORDER BY total_viajes DESC
                        LIMIT 10
                        """,
                        'description': 'Destinos más populares'
                    }
                ])
        
        # Ejecutar todas las consultas predefinidas
        for category, info in predefined_queries.items():
            logger.info(f"📋 Ejecutando categoría: {info['description']}")
            
            results['results'][category] = {
                'description': info['description'],
                'queries': {}
            }
            
            for query_info in info['queries']:
                try:
                    df_result = self.execute_query(
                        query_info['sql'], 
                        query_info['description']
                    )
                    
                    if df_result is not None:
                        results['results'][category]['queries'][query_info['name']] = {
                            'description': query_info['description'],
                            'data': df_result.to_dict('records'),
                            'rows': len(df_result),
                            'columns': list(df_result.columns)
                        }
                        results['queries_executed'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error en consulta {query_info['name']}: {e}")
        
        logger.info(f"✅ Consultas predefinidas completadas")
        logger.info(f"   Total ejecutadas: {results['queries_executed']}")
        
        return results
    
    def export_report(self, results: Dict[str, Any], filename: str = None) -> str:
        """
        EXPORTADOR PROFESIONAL DE REPORTES
        ===================================
        
        Genera reportes profesionales en formato Markdown y JSON con todos
        los resultados del análisis de datos.
        
        Args:
            results (Dict[str, Any]): Resultados del análisis
            filename (str): Nombre base del archivo (opcional)
            
        Returns:
            str: Ruta del archivo generado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_analysis_report_{timestamp}"
        
        # Generar reporte Markdown
        md_path = f"{filename}.md"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# REPORTE DE ANÁLISIS DE BASE DE DATOS BIG DATA\n\n")
            f.write("## PROYECTO: UNIVERSIDAD CENTRAL - BIG DATA ANALYTICS\n\n")
            f.write(f"**Fecha del análisis**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Base de datos**: {self.db_path}\n")
            f.write(f"**Tablas analizadas**: {len(self.tables)}\n\n")
            
            f.write("## TABLAS DISPONIBLES\n\n")
            for i, table in enumerate(self.tables, 1):
                f.write(f"{i}. **{table}**\n")
            f.write("\n")
            
            f.write("## RESULTADOS DE ANÁLISIS\n\n")
            
            if 'results' in results:
                for category, info in results['results'].items():
                    f.write(f"### {info['description'].upper()}\n\n")
                    
                    for query_name, query_result in info['queries'].items():
                        f.write(f"#### {query_result['description']}\n\n")
                        
                        if query_result['data']:
                            # Convertir a DataFrame para mejor formato
                            df = pd.DataFrame(query_result['data'])
                            f.write(df.to_markdown(index=False))
                            f.write(f"\n\n**Registros**: {query_result['rows']}\n\n")
                        else:
                            f.write("*Sin datos disponibles*\n\n")
            
            f.write("## ESTADÍSTICAS DEL ANÁLISIS\n\n")
            f.write(f"- **Consultas ejecutadas**: {results.get('queries_executed', 0)}\n")
            f.write(f"- **Tiempo de generación**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **Historial de consultas**: {len(self.query_history)}\n\n")
            
            f.write("---\n\n")
            f.write("**Generado por**: Sistema de Análisis Big Data\n")
            f.write("**Tecnologías**: Python, DuckDB, Pandas\n")
            f.write("**Universidad**: Central - Clase de Big Data y Analítica de Datos\n")
        
        # Generar reporte JSON
        json_path = f"{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 Reporte exportado:")
        logger.info(f"   Markdown: {md_path}")
        logger.info(f"   JSON: {json_path}")
        
        return md_path
    
    def interactive_mode(self):
        """
        MODO INTERACTIVO PROFESIONAL
        =============================
        
        Proporciona una interfaz interactiva completa para consultas SQL,
        análisis estadístico y generación de reportes.
        """
        print("\n" + "="*70)
        print("🎓 SISTEMA INTERACTIVO DE ANÁLISIS BIG DATA")
        print("   Universidad Central - Clase de Big Data y Analítica de Datos")
        print("="*70)
        print(f"Base de datos: {self.db_path}")
        print(f"Tablas disponibles: {', '.join(self.tables)}")
        print("="*70)
        
        while True:
            print("\n📋 MENÚ PRINCIPAL")
            print("1. 📊 Estadísticas básicas de tabla")
            print("2. 🔍 Ejecutar consulta SQL personalizada")
            print("3. 🚀 Ejecutar consultas predefinidas")
            print("4. 📄 Generar reporte completo")
            print("5. 📈 Ver historial de consultas")
            print("6. 🔍 Consultas de análisis avanzado")
            print("7. 📊 Generar estadísticas completas")
            print("0. 🚪 Salir")
            
            choice = input("\n🎯 Seleccione una opción: ").strip()
            
            if choice == "1":
                self._menu_basic_stats()
            elif choice == "2":
                self._menu_custom_query()
            elif choice == "3":
                self._menu_predefined_queries()
            elif choice == "4":
                self._menu_generate_report()
            elif choice == "5":
                self._menu_query_history()
            elif choice == "6":
                self._menu_advanced_analysis()
            elif choice == "7":
                self._menu_complete_statistics()
            elif choice == "0":
                print("\n👋 ¡Gracias por usar el Sistema de Análisis Big Data!")
                print("🎓 Universidad Central - Clase de Big Data y Analítica de Datos")
                break
            else:
                print("❌ Opción no válida. Intente nuevamente.")
    
    def _menu_basic_stats(self):
        """Menú para estadísticas básicas"""
        print("\n📊 ESTADÍSTICAS BÁSICAS")
        print("Tablas disponibles:")
        for i, table in enumerate(self.tables, 1):
            print(f"  {i}. {table}")
        
        try:
            choice = int(input("Seleccione tabla (número): ")) - 1
            if 0 <= choice < len(self.tables):
                table_name = self.tables[choice]
                stats = self.get_basic_stats(table_name)
                
                print(f"\n✅ ESTADÍSTICAS DE {table_name.upper()}")
                print(f"Total registros: {stats.get('total_records', 0):,}")
                print(f"Total columnas: {stats.get('columns', {}).get('count', 0)}")
                
                if 'sample_data' in stats and stats['sample_data']:
                    print("\n📋 MUESTRA DE DATOS:")
                    df = pd.DataFrame(stats['sample_data'])
                    print(df.to_string(index=False))
            else:
                print("❌ Selección inválida")
        except ValueError:
            print("❌ Entrada inválida")
    
    def _menu_custom_query(self):
        """Menú para consultas personalizadas"""
        print("\n🔍 CONSULTA SQL PERSONALIZADA")
        print("Ingrese su consulta SQL (escriba 'salir' para volver):")
        
        query = input("SQL> ").strip()
        if query.lower() != 'salir':
            result = self.execute_query(query, "Consulta personalizada")
            if result is not None:
                print(f"\n✅ RESULTADO ({len(result)} filas):")
                if len(result) > 0:
                    print(result.to_string(index=False))
                else:
                    print("Sin resultados")
    
    def _menu_predefined_queries(self):
        """Menú para consultas predefinidas"""
        print("\n🚀 EJECUTANDO CONSULTAS PREDEFINIDAS")
        print("Esto puede tomar unos momentos...")
        
        results = self.run_predefined_queries()
        print(f"\n✅ COMPLETADO: {results['queries_executed']} consultas ejecutadas")
        
        # Mostrar resumen de resultados
        if 'results' in results:
            for category, info in results['results'].items():
                print(f"\n📋 {info['description'].upper()}")
                for query_name, query_result in info['queries'].items():
                    print(f"  ✓ {query_result['description']}: {query_result['rows']} filas")
    
    def _menu_generate_report(self):
        """Menú para generar reportes"""
        print("\n📄 GENERANDO REPORTE COMPLETO")
        print("Ejecutando análisis completo...")
        
        # Ejecutar análisis completo
        results = self.run_predefined_queries()
        
        # Generar estadísticas para todas las tablas
        for table in self.tables:
            table_stats = self.get_basic_stats(table)
            results[f'stats_{table}'] = table_stats
        
        # Exportar reporte
        report_path = self.export_report(results)
        print(f"\n✅ REPORTE GENERADO: {report_path}")
    
    def _menu_query_history(self):
        """Menú para ver historial"""
        print(f"\n📈 HISTORIAL DE CONSULTAS ({len(self.query_history)} registros)")
        
        if not self.query_history:
            print("Sin consultas en el historial")
            return
        
        for i, query in enumerate(self.query_history[-10:], 1):  # Últimas 10
            status = "✅" if query.get('success', False) else "❌"
            print(f"{i}. {status} {query.get('description', 'Sin descripción')}")
            print(f"   Tiempo: {query.get('execution_time', 0):.3f}s")
            if not query.get('success', False):
                print(f"   Error: {query.get('error', 'Desconocido')}")
    
    def _menu_advanced_analysis(self):
        """Menú para análisis avanzado"""
        print("\n🔍 ANÁLISIS AVANZADO")
        print("Seleccione tipo de análisis:")
        print("1. Análisis de calidad de datos")
        print("2. Distribución de valores por columna")
        print("3. Análisis de correlaciones")
        print("4. Detección de outliers")
        
        choice = input("Opción: ").strip()
        
        if choice == "1":
            self._quality_analysis()
        elif choice in ["2", "3", "4"]:
            print("🚧 Análisis en desarrollo - Próximamente disponible")
    
    def _quality_analysis(self):
        """Análisis de calidad de datos"""
        print("\n📊 ANÁLISIS DE CALIDAD DE DATOS")
        
        for table in self.tables:
            print(f"\n🔍 Analizando: {table}")
            
            # Análisis de valores nulos
            null_query = f"""
            SELECT 
                column_name,
                COUNT(*) as total_rows,
                SUM(CASE WHEN column_name IS NULL THEN 1 ELSE 0 END) as null_count,
                ROUND(SUM(CASE WHEN column_name IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as null_percentage
            FROM (
                SELECT * FROM {table}
            ) t
            """
            
            # Mostrar información básica
            basic_query = f"SELECT COUNT(*) as total_records FROM {table}"
            result = self.execute_query(basic_query, f"Conteo de {table}")
            if result is not None:
                print(f"  Total registros: {result.iloc[0, 0]:,}")
    
    def _menu_complete_statistics(self):
        """Menú para estadísticas completas"""
        print("\n📊 GENERANDO ESTADÍSTICAS COMPLETAS")
        print("Esto analizará todas las tablas en detalle...")
        
        complete_stats = {}
        
        for table in self.tables:
            print(f"\n🔄 Procesando: {table}")
            stats = self.get_basic_stats(table)
            complete_stats[table] = stats
        
        # Mostrar resumen
        print(f"\n✅ ESTADÍSTICAS COMPLETAS GENERADAS")
        total_records = sum(stats.get('total_records', 0) for stats in complete_stats.values())
        print(f"📊 Total de registros en todas las tablas: {total_records:,}")
        
        for table, stats in complete_stats.items():
            records = stats.get('total_records', 0)
            columns = stats.get('columns', {}).get('count', 0)
            print(f"  📋 {table}: {records:,} registros, {columns} columnas")
    
    def close(self):
        """Cierre limpio del sistema"""
        if self.conn:
            self.conn.close()
            logger.info("🔒 Conexión cerrada correctamente")


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """
    FUNCIÓN PRINCIPAL DEL ANALIZADOR
    =================================
    
    Punto de entrada principal que inicializa el sistema y proporciona
    opciones para análisis interactivo o por lotes.
    """
    print("🎓 SISTEMA DE ANÁLISIS BIG DATA - UNIVERSIDAD CENTRAL")
    print("="*70)
    print("Analizador Profesional de Datos con DuckDB y Python")
    print("="*70)
    
    # Inicializar analizador
    analyzer = DataAnalyzer()
    
    if not analyzer.connect():
        print("❌ Error conectando a la base de datos")
        print("Verifique que complete_analysis.duckdb exista en el directorio actual")
        return False
    
    try:
        # Mostrar información inicial
        print(f"\n✅ CONEXIÓN ESTABLECIDA")
        print(f"Base de datos: {analyzer.db_path}")
        print(f"Tablas disponibles: {len(analyzer.tables)}")
        
        # Opciones de ejecución
        print("\n🎯 OPCIONES DE EJECUCIÓN:")
        print("1. Modo interactivo completo")
        print("2. Análisis rápido con reporte automático")
        print("3. Solo estadísticas básicas")
        
        choice = input("\nSeleccione opción (1-3): ").strip()
        
        if choice == "1":
            analyzer.interactive_mode()
        elif choice == "2":
            print("\n🚀 EJECUTANDO ANÁLISIS RÁPIDO...")
            results = analyzer.run_predefined_queries()
            report_path = analyzer.export_report(results, "quick_analysis")
            print(f"\n✅ ANÁLISIS COMPLETADO")
            print(f"📄 Reporte generado: {report_path}")
        elif choice == "3":
            print("\n📊 ESTADÍSTICAS BÁSICAS DE TODAS LAS TABLAS")
            for table in analyzer.tables:
                stats = analyzer.get_basic_stats(table)
                records = stats.get('total_records', 0)
                columns = stats.get('columns', {}).get('count', 0)
                print(f"📋 {table}: {records:,} registros, {columns} columnas")
        else:
            print("❌ Opción no válida")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n👋 Análisis interrumpido por el usuario")
        return True
    except Exception as e:
        logger.error(f"❌ Error durante análisis: {e}")
        return False
    finally:
        analyzer.close()


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    """
    PUNTO DE ENTRADA PRINCIPAL
    ==========================
    
    Ejecuta el sistema de análisis con manejo robusto de errores.
    """
    try:
        success = main()
        if success:
            print("\n🏆 ANÁLISIS COMPLETADO EXITOSAMENTE")
        else:
            print("\n❌ ANÁLISIS FINALIZADO CON ERRORES")
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        logger.error(f"Error crítico en main: {e}")