#!/usr/bin/env python3
"""
SISTEMA DE CONSULTAS INTERACTIVO - PARCIAL 1
=============================================
Sistema para realizar consultas SQL a la base de datos DuckDB
con 240,278 registros procesados completamente.
"""

import duckdb
import pandas as pd
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

class QuerySystem:
    """Sistema de consultas SQL interactivo para la base de datos completa"""
    
    def __init__(self, db_path: str = "complete_analysis.duckdb"):
        self.db_path = db_path
        self.conn = None
        self.tables = []
        
    def connect(self) -> bool:
        """Conectar a la base de datos DuckDB"""
        try:
            self.conn = duckdb.connect(self.db_path)
            print(f"✅ Conectado a: {self.db_path}")
            
            # Obtener lista de tablas
            self.tables = self.get_tables()
            print(f"📊 Tablas disponibles: {len(self.tables)}")
            for table in self.tables:
                count = self.get_table_count(table)
                print(f"   - {table}: {count:,} registros")
            
            return True
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return False
    
    def get_tables(self) -> List[str]:
        """Obtener lista de tablas"""
        try:
            result = self.conn.execute("SHOW TABLES").fetchall()
            return [row[0] for row in result]
        except Exception as e:
            print(f"❌ Error obteniendo tablas: {e}")
            return []
    
    def get_table_count(self, table_name: str) -> int:
        """Obtener número de registros de una tabla"""
        try:
            result = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            return result[0] if result else 0
        except:
            return 0
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Obtener información detallada de una tabla"""
        try:
            # Estructura de la tabla
            columns_info = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
            columns = [{"name": col[0], "type": col[1]} for col in columns_info]
            
            # Estadísticas básicas
            count = self.get_table_count(table_name)
            
            # Muestra de datos
            sample = self.conn.execute(f"SELECT * FROM {table_name} LIMIT 3").fetchall()
            column_names = [col["name"] for col in columns]
            sample_data = [dict(zip(column_names, row)) for row in sample]
            
            return {
                "table_name": table_name,
                "total_records": count,
                "columns": columns,
                "total_columns": len(columns),
                "sample_data": sample_data
            }
        except Exception as e:
            print(f"❌ Error obteniendo info de {table_name}: {e}")
            return {}
    
    def execute_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Ejecutar una consulta SQL"""
        start_time = time.time()
        
        try:
            print(f"🔍 Ejecutando consulta...")
            print(f"📝 SQL: {query}")
            
            # Ejecutar consulta
            result = self.conn.execute(query).fetchall()
            
            # Obtener nombres de columnas
            columns = [desc[0] for desc in self.conn.description] if self.conn.description else []
            
            # Convertir a lista de diccionarios
            data = []
            for row in result[:limit]:  # Limitar resultados para evitar sobrecarga
                data.append(dict(zip(columns, row)))
            
            execution_time = time.time() - start_time
            
            response = {
                "success": True,
                "execution_time": round(execution_time, 3),
                "total_rows": len(result),
                "returned_rows": len(data),
                "columns": columns,
                "data": data,
                "query": query
            }
            
            print(f"✅ Consulta exitosa: {len(result):,} filas en {execution_time:.3f}s")
            if len(result) > limit:
                print(f"📋 Mostrando primeras {limit} filas de {len(result):,} totales")
            
            return response
            
        except Exception as e:
            print(f"❌ Error en consulta: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "execution_time": time.time() - start_time
            }
    
    def show_sample_queries(self):
        """Mostrar consultas de ejemplo"""
        queries = {
            "1. Estadísticas básicas por tabla": [
                "SELECT COUNT(*) as total_facturas FROM facturas;",
                "SELECT COUNT(*) as total_historias FROM historias_clinicas;", 
                "SELECT COUNT(*) as total_tickets FROM ticketes_viajes;"
            ],
            
            "2. Análisis de Facturas": [
                "SELECT empresa_nombre, COUNT(*) as num_facturas FROM facturas GROUP BY empresa_nombre ORDER BY num_facturas DESC LIMIT 10;",
                "SELECT empresa_ciudad, COUNT(*) as facturas_ciudad FROM facturas GROUP BY empresa_ciudad ORDER BY facturas_ciudad DESC;",
                "SELECT DATE_TRUNC('month', fecha_hora::timestamp) as mes, COUNT(*) as facturas_mes FROM facturas GROUP BY mes ORDER BY mes;"
            ],
            
            "3. Análisis de Historias Clínicas": [
                "SELECT eps_nombre, COUNT(*) as num_pacientes FROM historias_clinicas GROUP BY eps_nombre ORDER BY num_pacientes DESC LIMIT 10;",
                "SELECT paciente_sexo, COUNT(*) as total FROM historias_clinicas GROUP BY paciente_sexo;",
                "SELECT EXTRACT(year FROM paciente_fecha_nacimiento::date) as año_nacimiento, COUNT(*) as pacientes FROM historias_clinicas GROUP BY año_nacimiento ORDER BY año_nacimiento DESC LIMIT 10;"
            ],
            
            "4. Análisis de Tickets de Viajes": [
                "SELECT empresa, COUNT(*) as num_tickets FROM ticketes_viajes GROUP BY empresa ORDER BY num_tickets DESC LIMIT 10;",
                "SELECT terminal_nombre, COUNT(*) as tickets_terminal FROM ticketes_viajes GROUP BY terminal_nombre ORDER BY tickets_terminal DESC LIMIT 10;",
                "SELECT ticket_tipo, COUNT(*) as total FROM ticketes_viajes GROUP BY ticket_tipo;"
            ],
            
            "5. Consultas Avanzadas Cross-Dataset": [
                "SELECT 'Facturas' as dataset, COUNT(*) as registros FROM facturas UNION ALL SELECT 'Historias' as dataset, COUNT(*) as registros FROM historias_clinicas UNION ALL SELECT 'Tickets' as dataset, COUNT(*) as registros FROM ticketes_viajes;",
                "SELECT f.empresa_ciudad, COUNT(f.*) as facturas, COUNT(DISTINCT f.empresa_nombre) as empresas FROM facturas f GROUP BY f.empresa_ciudad ORDER BY facturas DESC LIMIT 15;"
            ]
        }
        
        print("\n" + "="*60)
        print("🔍 CONSULTAS DE EJEMPLO - BASE DE DATOS COMPLETA")
        print("="*60)
        
        for category, query_list in queries.items():
            print(f"\n📊 {category}")
            print("-" * 50)
            for i, query in enumerate(query_list, 1):
                print(f"{i}. {query}")
        
        print(f"\n💡 CONSEJOS:")
        print("• Usa LIMIT para consultas grandes")
        print("• Los nombres de tablas: facturas, historias_clinicas, ticketes_viajes")  
        print("• Total de registros disponibles: 240,278")
        print("• Base de datos optimizada para consultas rápidas")
    
    def interactive_mode(self):
        """Modo interactivo para consultas"""
        print("\n" + "="*60)
        print("🚀 MODO INTERACTIVO DE CONSULTAS SQL")
        print("="*60)
        print("Comandos disponibles:")
        print("• 'info [tabla]' - Información de tabla")
        print("• 'examples' - Ver consultas de ejemplo")
        print("• 'tables' - Listar todas las tablas")
        print("• 'quit' o 'exit' - Salir")
        print("• O escribe cualquier consulta SQL")
        print("-" * 60)
        
        while True:
            try:
                query = input("\n🔍 SQL> ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 ¡Adiós!")
                    break
                    
                elif query.lower() == 'examples':
                    self.show_sample_queries()
                    
                elif query.lower() == 'tables':
                    print(f"\n📊 Tablas disponibles:")
                    for table in self.tables:
                        count = self.get_table_count(table)
                        print(f"   • {table}: {count:,} registros")
                        
                elif query.lower().startswith('info'):
                    parts = query.split()
                    if len(parts) > 1:
                        table_name = parts[1]
                        if table_name in self.tables:
                            info = self.get_table_info(table_name)
                            print(f"\n📋 Información de {table_name}:")
                            print(f"   • Registros: {info['total_records']:,}")
                            print(f"   • Columnas: {info['total_columns']}")
                            print("   • Estructura:")
                            for col in info['columns'][:10]:  # Mostrar max 10 columnas
                                print(f"     - {col['name']}: {col['type']}")
                            if len(info['columns']) > 10:
                                print(f"     ... y {len(info['columns'])-10} columnas más")
                        else:
                            print(f"❌ Tabla '{table_name}' no encontrada")
                    else:
                        print("💡 Uso: info [nombre_tabla]")
                        
                else:
                    # Ejecutar consulta SQL
                    result = self.execute_query(query)
                    
                    if result['success'] and result['data']:
                        print(f"\n📊 Resultados ({result['returned_rows']} filas):")
                        
                        # Mostrar datos en formato tabla
                        df = pd.DataFrame(result['data'])
                        print(df.to_string(index=False, max_rows=10))
                        
                        if result['total_rows'] > 10:
                            print(f"\n... y {result['total_rows']-10} filas más")
                            
            except KeyboardInterrupt:
                print("\n👋 ¡Adiós!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
            print("🔌 Conexión cerrada")

def main():
    """Función principal"""
    print("="*60)
    print("🗄️  SISTEMA DE CONSULTAS - BASE DE DATOS COMPLETA")
    print("="*60)
    print("📊 240,278 registros en 3 tablas")
    print("⚡ Sistema optimizado para consultas rápidas")
    print("="*60)
    
    # Verificar si existe la base de datos
    db_path = "complete_analysis.duckdb"
    if not Path(db_path).exists():
        print(f"❌ Base de datos no encontrada: {db_path}")
        print("💡 Ejecuta primero complete_all_processor.py")
        return False
    
    # Crear sistema de consultas
    query_system = QuerySystem(db_path)
    
    try:
        # Conectar
        if not query_system.connect():
            return False
        
        # Mostrar consultas de ejemplo
        query_system.show_sample_queries()
        
        # Iniciar modo interactivo
        query_system.interactive_mode()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        query_system.close()
    
    return True

if __name__ == "__main__":
    main()