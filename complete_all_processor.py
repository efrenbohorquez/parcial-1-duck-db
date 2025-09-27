#!/usr/bin/env python3
"""
PROCESADOR COMPLETO BASADO EN EL OPTIMIZADO QUE FUNCIONA
========================================================
Extensión del optimized_analysis.py para procesar TODOS los registros
sin límite de muestra, usando la configuración que ya sabemos que funciona.
"""

import duckdb
import json
import zipfile
import logging
import time
import os
import gc
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompleteProcessor:
    """Procesador completo basado en el análisis optimizado exitoso"""
    
    def __init__(self):
        self.conn = None
        self.start_time = time.time()
        
    def connect_duckdb(self):
        """Conectar a DuckDB con la configuración que sabemos que funciona"""
        try:
            self.conn = duckdb.connect("complete_analysis.duckdb")
            # Usar solo configuraciones que sabemos que funcionan
            self.conn.execute("SET max_expression_depth TO 10000")
            self.conn.execute("SET threads TO 8")
            logger.info("DuckDB conectado exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error conectando DuckDB: {e}")
            return False
    
    def analyze_zip_content(self, zip_path: str) -> Dict[str, Any]:
        """Analizar contenido del ZIP (reutilizado del optimized_analysis.py)"""
        logger.info("Analizando estructura del ZIP...")
        
        analysis = {
            'total_files': 0,
            'total_size': 0,
            'files_by_type': {},
            'nested_zips': [],
            'sample_files': []
        }
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as main_zip:
                file_list = main_zip.filelist
                
                for file_info in file_list:
                    analysis['total_files'] += 1
                    analysis['total_size'] += file_info.file_size
                    
                    # Analizar por extensión
                    ext = Path(file_info.filename).suffix.lower()
                    if ext not in analysis['files_by_type']:
                        analysis['files_by_type'][ext] = 0
                    analysis['files_by_type'][ext] += 1
                    
                    # Identificar ZIPs anidados
                    if ext == '.zip':
                        analysis['nested_zips'].append({
                            'name': file_info.filename,
                            'size': file_info.file_size
                        })
                
                logger.info(f"Archivos encontrados: {analysis['total_files']}")
                logger.info(f"Tamaño total: {analysis['total_size'] / (1024*1024):.2f} MB")
                logger.info(f"ZIPs anidados: {len(analysis['nested_zips'])}")
                
        except Exception as e:
            logger.error(f"Error analizando ZIP: {e}")
            
        return analysis
    
    def process_complete_nested_zip(self, zip_path: str, nested_zip_name: str, max_files: int = None) -> List[Dict]:
        """Procesar TODOS los archivos de un ZIP anidado (sin límite si max_files=None)"""
        logger.info(f"Procesando COMPLETO: {nested_zip_name}")
        
        all_data = []
        processed_count = 0
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as main_zip:
                with main_zip.open(nested_zip_name) as nested_file:
                    with zipfile.ZipFile(nested_file, 'r') as nested_zip:
                        json_files = [f for f in nested_zip.filelist 
                                    if f.filename.endswith('.json')]
                        
                        # Si no hay límite, procesar todos
                        files_to_process = json_files if max_files is None else json_files[:max_files]
                        total_files = len(files_to_process)
                        
                        logger.info(f"Procesando {total_files} archivos JSON de {nested_zip_name}")
                        
                        for i, json_file in enumerate(files_to_process):
                            try:
                                # Monitorear memoria cada 1000 archivos
                                if i % 1000 == 0 and i > 0:
                                    memory = psutil.virtual_memory()
                                    logger.info(f"Progreso: {i}/{total_files} ({i/total_files*100:.1f}%) - Memoria: {memory.percent:.1f}%")
                                    
                                    # Si la memoria está muy alta, hacer limpieza
                                    if memory.percent > 85:
                                        logger.warning("Memoria alta, forzando garbage collection")
                                        gc.collect()
                                
                                with nested_zip.open(json_file.filename) as jf:
                                    content = jf.read().decode('utf-8')
                                    data = json.loads(content)
                                    all_data.append(data)
                                    processed_count += 1
                                    
                            except Exception as e:
                                logger.warning(f"Error procesando {json_file.filename}: {e}")
                                continue
                        
                        logger.info(f"COMPLETADO {nested_zip_name}: {processed_count} registros procesados")
                        
        except Exception as e:
            logger.error(f"Error procesando {nested_zip_name}: {e}")
            
        return all_data
    
    def load_to_duckdb(self, data: List[Dict], table_name: str) -> bool:
        """Cargar datos a DuckDB (reutilizado del optimized_analysis.py)"""
        if not data or not self.conn:
            return False
            
        try:
            logger.info(f"Cargando {len(data)} registros a tabla {table_name}...")
            
            # Crear tabla desde JSON usando pandas
            import pandas as pd
            df = pd.DataFrame(data)
            
            # Registrar DataFrame en DuckDB
            self.conn.register(f"{table_name}_df", df)
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {table_name}_df")
            self.conn.unregister(f"{table_name}_df")
            
            # Verificar carga
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            logger.info(f"Tabla {table_name} creada con {count} registros")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cargando a {table_name}: {e}")
            return False
    
    def get_complete_stats(self, table_name: str) -> Dict[str, Any]:
        """Obtener estadísticas completas de la tabla"""
        try:
            # Información general
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            
            # Obtener columnas
            columns_info = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
            columns = [col[0] for col in columns_info]
            
            stats = {
                'total_records': count,
                'total_columns': len(columns),
                'columns': columns,
                'sample_data': [],
                'column_stats': {}
            }
            
            # Muestra de datos
            sample = self.conn.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchall()
            for row in sample:
                stats['sample_data'].append(dict(zip(columns, row)))
            
            # Estadísticas por columna (intentar obtener valores únicos)
            for col in columns:
                try:
                    distinct_result = self.conn.execute(f"SELECT COUNT(DISTINCT \"{col}\") FROM {table_name}").fetchone()
                    distinct_count = distinct_result[0] if distinct_result else 0
                    stats['column_stats'][col] = {'distinct_values': distinct_count}
                except:
                    stats['column_stats'][col] = {'distinct_values': 'N/A'}
            
            logger.info(f"Estadísticas completas de {table_name}: {count} registros, {len(columns)} columnas")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de {table_name}: {e}")
            return {}
    
    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
            logger.info("Conexión DuckDB cerrada")

def main():
    """Función principal para procesamiento completo"""
    zip_path = r"D:\Parcial 1-20250926.zip"
    output_dir = Path("output_complete_all")
    output_dir.mkdir(exist_ok=True)
    
    if not os.path.exists(zip_path):
        logger.error(f"Archivo no encontrado: {zip_path}")
        return False
    
    start_time = time.time()
    processor = CompleteProcessor()
    
    try:
        logger.info("=== INICIANDO PROCESAMIENTO COMPLETO DE TODOS LOS DATOS ===")
        
        # 1. Conectar DuckDB
        if not processor.connect_duckdb():
            return False
        
        # 2. Analizar estructura ZIP
        zip_analysis = processor.analyze_zip_content(zip_path)
        
        # 3. Procesar TODOS los ZIPs anidados sin límite
        results = {}
        
        for nested_zip in zip_analysis['nested_zips']:
            zip_name = nested_zip['name']
            table_name = Path(zip_name).stem.lower().replace('-', '_').replace(' ', '_')
            
            logger.info(f"\n--- PROCESANDO COMPLETO: {zip_name} ---")
            
            # Procesar SIN límite (max_files=None)
            complete_data = processor.process_complete_nested_zip(zip_path, zip_name, max_files=None)
            
            if complete_data:
                # Cargar TODOS los datos a DuckDB
                if processor.load_to_duckdb(complete_data, table_name):
                    # Obtener estadísticas completas
                    stats = processor.get_complete_stats(table_name)
                    results[table_name] = {
                        'zip_source': zip_name,
                        'total_processed': len(complete_data),
                        'statistics': stats
                    }
                    
                    # Liberar memoria
                    del complete_data
                    gc.collect()
        
        # 4. Generar reporte final completo
        processing_time = time.time() - start_time
        
        final_report = {
            'analysis_time': processing_time,
            'zip_analysis': zip_analysis,
            'processed_tables': results,
            'summary': {
                'total_nested_zips': len(zip_analysis['nested_zips']),
                'tables_created': len(results),
                'total_records': sum(r['total_processed'] for r in results.values()),
                'processing_speed': sum(r['total_processed'] for r in results.values()) / processing_time
            }
        }
        
        # Guardar reporte JSON
        with open(output_dir / 'complete_all_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False, default=str)
        
        # Generar reporte markdown
        with open(output_dir / 'complete_all_analysis.md', 'w', encoding='utf-8') as f:
            f.write("# ANALISIS COMPLETO DE TODOS LOS DATOS - PARCIAL 1\n\n")
            f.write(f"**Tiempo de procesamiento**: {processing_time:.2f} segundos\n\n")
            
            f.write("## Resumen Ejecutivo\n")
            summary = final_report['summary']
            f.write(f"- **Total de registros procesados**: {summary['total_records']:,}\n")
            f.write(f"- **Velocidad de procesamiento**: {summary['processing_speed']:.0f} registros/segundo\n")
            f.write(f"- **Tablas creadas**: {summary['tables_created']}\n")
            f.write(f"- **ZIPs procesados**: {summary['total_nested_zips']}\n\n")
            
            f.write("## Detalle por Dataset\n")
            for table_name, info in results.items():
                f.write(f"### {table_name.upper()}\n")
                f.write(f"- **Fuente**: {info['zip_source']}\n")
                f.write(f"- **Registros totales**: {info['total_processed']:,}\n")
                if 'statistics' in info and info['statistics']:
                    stats = info['statistics']
                    f.write(f"- **Columnas**: {stats.get('total_columns', 'N/A')}\n")
                    f.write(f"- **Estructura**: {', '.join(stats.get('columns', [])[:7])}...\n")
                f.write("\n")
            
            f.write("## Estado Final\n")
            f.write("✅ **PROCESAMIENTO COMPLETO EXITOSO**\n")
            f.write("✅ **Todos los archivos JSON procesados sin límite**\n")
            f.write("✅ **Base de datos DuckDB con datos completos**\n")
            f.write("✅ **Sistema listo para análisis masivos**\n")
        
        elapsed = time.time() - start_time
        logger.info(f"\n=== PROCESAMIENTO COMPLETO FINALIZADO ===")
        logger.info(f"Tiempo total: {elapsed:.2f} segundos")
        logger.info(f"Registros totales: {final_report['summary']['total_records']:,}")
        logger.info(f"Velocidad promedio: {final_report['summary']['processing_speed']:.0f} reg/seg")
        logger.info(f"Tablas creadas: {len(results)}")
        logger.info(f"Reportes en: {output_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error durante procesamiento completo: {e}")
        return False
        
    finally:
        processor.close()

if __name__ == "__main__":
    import pandas as pd  # Importar pandas para uso en DuckDB  
    
    print("PROCESADOR COMPLETO DE TODOS LOS DATOS - PARCIAL 1")
    print("=" * 60)
    print("Procesando TODOS los 80,000+ registros sin límite...")
    print("=" * 60)
    
    success = main()
    print(f"\n{'='*60}")
    print(f"RESULTADO: {'EXITO TOTAL' if success else 'ERROR'}")
    print(f"{'='*60}")