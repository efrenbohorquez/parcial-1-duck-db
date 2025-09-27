"""
Script de instalación y configuración automática para el proyecto de análisis de datos.
Ejecuta este script para configurar el entorno completo.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Mostrar banner de bienvenida."""
    print("=" * 60)
    print("📊 INSTALADOR DE PROYECTO DE ANÁLISIS DE DATOS JSON")
    print("=" * 60)
    print()

def check_python_version():
    """Verificar versión de Python."""
    print("🔍 Verificando versión de Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
    return True

def create_directories():
    """Crear directorios necesarios."""
    print("\n📁 Creando directorios...")
    
    directories = [
        'data',
        'data/extracted', 
        'reports',
        'config',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")
    
    print("✅ Directorios creados exitosamente")

def install_dependencies():
    """Instalar dependencias de Python."""
    print("\n📦 Instalando dependencias de Python...")
    
    try:
        # Actualizar pip
        print("   Actualizando pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Instalar dependencias
        print("   Instalando paquetes...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        print("✅ Dependencias instaladas exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        print("   Intenta instalar manualmente con: pip install -r requirements.txt")
        return False

def verify_installation():
    """Verificar que las dependencias principales estén instaladas."""
    print("\n🔍 Verificando instalación...")
    
    required_packages = [
        ('duckdb', 'DuckDB'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('plotly', 'Plotly'),
        ('matplotlib', 'Matplotlib'),
        ('seaborn', 'Seaborn'),
        ('scipy', 'SciPy'),
        ('sklearn', 'Scikit-learn')
    ]
    
    all_installed = True
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - No instalado")
            all_installed = False
    
    return all_installed

def create_sample_config():
    """Crear archivo de configuración de ejemplo."""
    print("\n⚙️ Creando configuración de ejemplo...")
    
    # Buscar archivo ZIP en ubicaciones comunes
    possible_paths = [
        "D:/Parcial 1-20250926.zip",
        "C:/Parcial 1-20250926.zip", 
        "./Parcial 1-20250926.zip",
        "./data/Parcial 1-20250926.zip"
    ]
    
    zip_path = None
    for path in possible_paths:
        if os.path.exists(path):
            zip_path = path
            break
    
    if not zip_path:
        zip_path = input("📁 Ingresa la ruta completa al archivo ZIP con datos: ")
        if not os.path.exists(zip_path):
            print(f"⚠️  Advertencia: El archivo {zip_path} no existe")
    
    config = {
        "zip_path": zip_path,
        "extract_path": "data/extracted",
        "db_path": "data/analytics.duckdb",
        "table_name": "json_data",
        "output_dir": "reports",
        "sample_size": 10000
    }
    
    config_path = Path("config/user_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, indent=2, fp=f)
    
    print(f"✅ Configuración guardada en: {config_path}")
    return str(config_path)

def run_test_analysis():
    """Ejecutar análisis de prueba."""
    print("\n🧪 ¿Deseas ejecutar un análisis de prueba? (s/n): ", end="")
    
    if input().lower().startswith('s'):
        print("\n🚀 Ejecutando análisis de prueba...")
        
        try:
            # Ejecutar análisis con configuración de ejemplo
            result = subprocess.run([
                sys.executable, 
                "main.py", 
                "--config", 
                "config/user_config.json",
                "--sample-size", 
                "1000"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Análisis de prueba completado exitosamente")
                print("📊 Revisa la carpeta 'reports/' para ver los resultados")
            else:
                print("❌ Error en análisis de prueba:")
                print(result.stderr)
                
        except subprocess.TimeoutExpired:
            print("⏰ El análisis de prueba tardó demasiado - pero la instalación está OK")
        except Exception as e:
            print(f"❌ Error ejecutando análisis de prueba: {e}")

def show_next_steps():
    """Mostrar pasos siguientes."""
    print("\n" + "=" * 60)
    print("🎉 ¡INSTALACIÓN COMPLETADA!")
    print("=" * 60)
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("1. Verifica que el archivo ZIP esté en la ruta correcta")
    print("2. Ejecuta el análisis:")
    print("   python main.py")
    print()
    print("3. O con configuración personalizada:")
    print("   python main.py --config config/user_config.json")
    print()
    print("4. Abre el dashboard generado:")
    print("   reports/dashboard.html")
    print()
    print("📚 COMANDOS ÚTILES:")
    print("   python main.py --help                    # Ver todas las opciones")
    print("   python main.py --sample-size 5000        # Análisis más rápido")
    print("   python main.py --output-dir mi_reporte   # Cambiar directorio de salida")
    print()
    print("🔧 SOPORTE:")
    print("   - Revisa README.md para documentación completa")
    print("   - Los logs se guardan en analysis.log")
    print()

def main():
    """Función principal del instalador."""
    print_banner()
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Crear directorios
    create_directories()
    
    # Instalar dependencias
    if not install_dependencies():
        print("⚠️  Continúando sin instalar dependencias...")
    
    # Verificar instalación
    if not verify_installation():
        print("⚠️  Algunas dependencias no están disponibles")
        print("   Instala manualmente con: pip install -r requirements.txt")
    
    # Crear configuración
    config_path = create_sample_config()
    
    # Análisis de prueba opcional
    run_test_analysis()
    
    # Mostrar próximos pasos
    show_next_steps()

if __name__ == "__main__":
    main()