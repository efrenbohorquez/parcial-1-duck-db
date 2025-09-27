#!/usr/bin/env python3
"""
SISTEMA DE CONSULTAS Y ESTADÍSTICAS PARA BASE DE DATOS COMPLETA
==============================================================
Sistema interactivo para realizar consultas SQL y generar estadísticas
de los 240,278 registros procesados en DuckDB
"""

import duckdb
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Analizador completo de datos con consultas SQL y estadísticas"""
    
    def __init__(self, db_path="complete_analysis.duckdb"):
        self.db_path = db_path
        self.conn = None
        self.tables_info = {}
        
    def connect(self):
        """Conectar a la base de datos DuckDB"""
        try:
            self.conn = duckdb.connect(self.db_path)
            logger.info(f"Conectado a base de datos: {self.db_path}")
            self._load_tables_info()
            return True
        except Exception as e:
            logger.error(f"Error conectando a base de datos: {e}")
            return False
    
    def _load_tables_info(self):
        """Cargar información de las tablas disponibles"""
        tables = self.conn.execute("SHOW TABLES").fetchall()
        
        for table in tables:
            table_name = table[0]
            
            # Obtener información de columnas
            columns_info = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
            
            # Contar registros
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            
            self.tables_info[table_name] = {
                'columns': [(col[0], col[1]) for col in columns_info],
                'record_count': count
            }
            
        logger.info(f"Tablas cargadas: {list(self.tables_info.keys())}")
    
    def show_database_info(self):
        """Mostrar información general de la base de datos"""
        print("\n" + "="*60)
        print("📊 INFORMACIÓN DE LA BASE DE DATOS")
        print("="*60)
        
        total_records = sum(info['record_count'] for info in self.tables_info.values())
        print(f"🗂️  Total de tablas: {len(self.tables_info)}")
        print(f"📈 Total de registros: {total_records:,}")
        
        print("\n📋 DETALLE POR TABLA:")
        for table_name, info in self.tables_info.items():
            print(f"\n  🔹 {table_name.upper()}")
            print(f"     📊 Registros: {info['record_count']:,}")
            print(f"     📝 Columnas: {len(info['columns'])}")
            print(f"     🏗️  Estructura: {', '.join([col[0] for col in info['columns'][:5]])}...")
    
    def execute_query(self, query, show_results=True, limit=10):
        """Ejecutar consulta SQL personalizada"""
        try:
            logger.info(f"Ejecutando consulta: {query[:50]}...")
            
            result = self.conn.execute(query).fetchall()
            
            if show_results:
                print(f"\n🔍 RESULTADO DE CONSULTA:")
                print(f"📊 Registros encontrados: {len(result)}")
                
                if result:
                    # Obtener nombres de columnas
                    columns = [desc[0] for desc in self.conn.description]
                    
                    print(f"\n📋 PRIMEROS {min(len(result), limit)} RESULTADOS:")
                    print("-" * 80)
                    
                    # Mostrar encabezados
                    header = " | ".join(f"{col[:12]:<12}" for col in columns)
                    print(header)
                    print("-" * len(header))
                    
                    # Mostrar datos
                    for i, row in enumerate(result[:limit]):
                        row_str = " | ".join(f"{str(val)[:12]:<12}" for val in row)
                        print(row_str)
            
            return result
            
        except Exception as e:
            logger.error(f"Error en consulta: {e}")
            print(f"❌ Error: {e}")
            return None
    
    def get_basic_stats(self, table_name):
        """Obtener estadísticas básicas de una tabla"""
        print(f"\n📊 ESTADÍSTICAS BÁSICAS - {table_name.upper()}")
        print("="*50)
        
        try:
            # Información general
            info = self.tables_info[table_name]
            print(f"📈 Total de registros: {info['record_count']:,}")
            print(f"📝 Total de columnas: {len(info['columns'])}")
            
            # Estadísticas por columna
            print(f"\n🔍 ANÁLISIS POR COLUMNA:")
            for col_name, col_type in info['columns']:
                try:
                    # Valores únicos
                    unique_query = f"SELECT COUNT(DISTINCT \"{col_name}\") FROM {table_name}"
                    unique_count = self.conn.execute(unique_query).fetchone()[0]
                    
                    # Valores nulos
                    null_query = f"SELECT COUNT(*) FROM {table_name} WHERE \"{col_name}\" IS NULL"
                    null_count = self.conn.execute(null_query).fetchone()[0]
                    
                    print(f"  🔹 {col_name} ({col_type})")
                    print(f"     - Valores únicos: {unique_count:,}")
                    print(f"     - Valores nulos: {null_count:,}")
                    
                    # Para columnas numéricas, obtener min/max
                    if 'int' in col_type.lower() or 'float' in col_type.lower() or 'double' in col_type.lower():
                        try:
                            stats_query = f"SELECT MIN(\"{col_name}\"), MAX(\"{col_name}\"), AVG(\"{col_name}\") FROM {table_name}"
                            min_val, max_val, avg_val = self.conn.execute(stats_query).fetchone()
                            print(f"     - Rango: {min_val} - {max_val}")
                            print(f"     - Promedio: {avg_val:.2f}" if avg_val else "     - Promedio: N/A")
                        except:
                            pass
                    
                except Exception as e:
                    print(f"  🔹 {col_name} ({col_type}) - Error al analizar")
                    
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
    
    def get_top_values(self, table_name, column_name, limit=10):
        """Obtener los valores más frecuentes de una columna"""
        try:
            query = f"""
            SELECT "{column_name}", COUNT(*) as frequency
            FROM {table_name}
            GROUP BY "{column_name}"
            ORDER BY frequency DESC
            LIMIT {limit}
            """
            
            print(f"\n🏆 TOP {limit} VALORES MÁS FRECUENTES - {column_name}")
            print("-" * 50)
            
            result = self.conn.execute(query).fetchall()
            
            for i, (value, freq) in enumerate(result, 1):
                percentage = (freq / self.tables_info[table_name]['record_count']) * 100
                print(f"{i}. {str(value)[:30]:<30} | {freq:>8,} ({percentage:>5.1f}%)")
                
        except Exception as e:
            logger.error(f"Error obteniendo top values: {e}")
    
    def generate_cross_analysis(self):
        """Generar análisis cruzado entre tablas"""
        print(f"\n🔄 ANÁLISIS CRUZADO ENTRE DATASETS")
        print("="*50)
        
        # Análisis temporal si hay fechas
        try:
            # Buscar columnas de fecha en cada tabla
            date_columns = {}
            for table_name, info in self.tables_info.items():
                for col_name, col_type in info['columns']:
                    if 'fecha' in col_name.lower() or 'date' in col_name.lower():
                        date_columns[table_name] = col_name
                        break
            
            if date_columns:
                print(f"\n📅 ANÁLISIS TEMPORAL:")
                for table_name, col_name in date_columns.items():
                    try:
                        query = f"""
                        SELECT 
                            strftime('%Y-%m', "{col_name}") as periodo,
                            COUNT(*) as registros
                        FROM {table_name}
                        GROUP BY periodo
                        ORDER BY periodo
                        LIMIT 12
                        """
                        result = self.conn.execute(query).fetchall()
                        
                        print(f"\n  🔹 {table_name.upper()} - Registros por mes:")
                        for periodo, count in result:
                            print(f"     {periodo}: {count:,} registros")
                            
                    except Exception as e:
                        print(f"     Error analizando {table_name}: {e}")
            
        except Exception as e:
            logger.error(f"Error en análisis cruzado: {e}")
    
    def export_summary_report(self, output_file="database_analysis_report.md"):
        """Exportar reporte completo en Markdown"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# REPORTE DE ANÁLISIS COMPLETO DE BASE DE DATOS\n\n")
                f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Resumen general
                total_records = sum(info['record_count'] for info in self.tables_info.values())
                f.write("## RESUMEN EJECUTIVO\n\n")
                f.write(f"- **Total de registros**: {total_records:,}\n")
                f.write(f"- **Total de tablas**: {len(self.tables_info)}\n")
                f.write(f"- **Base de datos**: {self.db_path}\n\n")
                
                # Detalle por tabla
                f.write("## DETALLE POR TABLA\n\n")
                for table_name, info in self.tables_info.items():
                    f.write(f"### {table_name.upper()}\n\n")
                    f.write(f"- **Registros**: {info['record_count']:,}\n")
                    f.write(f"- **Columnas**: {len(info['columns'])}\n")
                    f.write("- **Estructura**:\n")
                    for col_name, col_type in info['columns']:
                        f.write(f"  - `{col_name}` ({col_type})\n")
                    f.write("\n")
                
                # Consultas de ejemplo
                f.write("## CONSULTAS DE EJEMPLO\n\n")
                f.write("```sql\n")
                f.write("-- Contar registros por tabla\n")
                for table_name in self.tables_info.keys():
                    f.write(f"SELECT COUNT(*) FROM {table_name};\n")
                f.write("\n-- Obtener muestra de datos\n")
                for table_name in self.tables_info.keys():
                    f.write(f"SELECT * FROM {table_name} LIMIT 5;\n")
                f.write("```\n\n")
                
            logger.info(f"Reporte exportado: {output_file}")
            print(f"\n✅ Reporte exportado: {output_file}")
            
        except Exception as e:
            logger.error(f"Error exportando reporte: {e}")
    
    def run_predefined_queries(self):
        """Ejecutar consultas predefinidas útiles"""
        print(f"\n🎯 EJECUTANDO CONSULTAS PREDEFINIDAS")
        print("="*50)
        
        queries = [
            {
                "name": "Resumen de registros por tabla",
                "query": """
                SELECT 'facturas' as tabla, COUNT(*) as total FROM facturas
                UNION ALL
                SELECT 'historias_clinicas' as tabla, COUNT(*) as total FROM historias_clinicas
                UNION ALL  
                SELECT 'ticketes_viajes' as tabla, COUNT(*) as total FROM ticketes_viajes
                """
            },
            {
                "name": "Top 5 empresas en facturas",
                "query": "SELECT empresa_nombre, COUNT(*) as facturas FROM facturas GROUP BY empresa_nombre ORDER BY facturas DESC LIMIT 5"
            },
            {
                "name": "Distribución por sexo en historias clínicas",
                "query": "SELECT paciente_sexo, COUNT(*) as pacientes FROM historias_clinicas GROUP BY paciente_sexo"
            },
            {
                "name": "Top 5 empresas de transporte",
                "query": "SELECT empresa, COUNT(*) as tickets FROM ticketes_viajes GROUP BY empresa ORDER BY tickets DESC LIMIT 5"
            }
        ]
        
        for i, query_info in enumerate(queries, 1):
            print(f"\n{i}️⃣ {query_info['name'].upper()}:")
            print("-" * 40)
            self.execute_query(query_info['query'], limit=15)
    
    def interactive_mode(self):
        """Modo interactivo para consultas"""
        print(f"\n🚀 MODO INTERACTIVO ACTIVADO")
        print("Escribe consultas SQL o comandos especiales:")
        print("  - 'info' : Mostrar información de la base")
        print("  - 'tables' : Listar tablas")
        print("  - 'stats TABLA' : Estadísticas de una tabla")
        print("  - 'top TABLA COLUMNA' : Top valores de una columna")
        print("  - 'export' : Exportar reporte")
        print("  - 'queries' : Ejecutar consultas predefinidas")
        print("  - 'exit' : Salir")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n🔍 SQL> ").strip()
                
                if not query:
                    continue
                    
                if query.lower() == 'exit':
                    break
                elif query.lower() == 'info':
                    self.show_database_info()
                elif query.lower() == 'tables':
                    print("\n📋 TABLAS DISPONIBLES:")
                    for table_name in self.tables_info.keys():
                        print(f"  - {table_name}")
                elif query.lower() == 'queries':
                    self.run_predefined_queries()
                elif query.lower().startswith('stats '):
                    table_name = query.split()[1].lower()
                    if table_name in self.tables_info:
                        self.get_basic_stats(table_name)
                    else:
                        print(f"❌ Tabla '{table_name}' no encontrada")
                elif query.lower().startswith('top '):
                    parts = query.split()
                    if len(parts) >= 3:
                        table_name, column_name = parts[1].lower(), parts[2]
                        if table_name in self.tables_info:
                            self.get_top_values(table_name, column_name)
                        else:
                            print(f"❌ Tabla '{table_name}' no encontrada")
                elif query.lower() == 'export':
                    self.export_summary_report()
                else:
                    # Ejecutar consulta SQL
                    self.execute_query(query)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 Sesión terminada")
    
    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
            logger.info("Conexión cerrada")

def main():
    """Función principal del sistema de consultas"""
    print("🎯 SISTEMA DE CONSULTAS Y ESTADÍSTICAS")
    print("="*60)
    
    analyzer = DataAnalyzer()
    
    try:
        if analyzer.connect():
            # Mostrar información inicial
            analyzer.show_database_info()
            
            # Ejecutar consultas predefinidas
            analyzer.run_predefined_queries()
            
            # Estadísticas básicas de cada tabla
            for table_name in analyzer.tables_info.keys():
                analyzer.get_basic_stats(table_name)
            
            # Análisis cruzado
            analyzer.generate_cross_analysis()
            
            # Exportar reporte
            analyzer.export_summary_report()
            
            # Modo interactivo
            analyzer.interactive_mode()
            
    except Exception as e:
        logger.error(f"Error en main: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()