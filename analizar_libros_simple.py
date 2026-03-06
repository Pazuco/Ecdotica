#!/usr/bin/env python3
"""
📚 SCRIPT SIMPLE PARA ANALIZAR LIBROS

USO:
1. Pon tus libros (PDF o DOCX) en la carpeta 'uploads/'
2. Ejecuta: python analizar_libros_simple.py
3. Los reportes se guardarán en 'reports/'

¡Así de simple!
"""

import sys
import asyncio
from pathlib import Path

try:
    from backend.services.book_processor import BookProcessor
except ImportError:
    print("❌ Error: No se encontró el módulo book_processor")
    print("\n✅ Solución:")
    print("   1. Asegúrate de estar en la carpeta del proyecto")
    print("   2. Instala dependencias: pip install -r requirements/base.txt")
    print("   3. Descarga modelo SpaCy: python -m spacy download es_core_news_sm")
    sys.exit(1)


def crear_carpetas():
    """Crear carpetas necesarias"""
    Path("uploads").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    print("✅ Carpetas 'uploads' y 'reports' listas")


def listar_libros():
    """Encontrar todos los libros en uploads/"""
    uploads_dir = Path("uploads")
    libros = []
    
    for extension in ['*.pdf', '*.docx', '*.doc']:
        libros.extend(uploads_dir.glob(extension))
    
    return libros


async def main():
    print("\n" + "="*60)
    print("📚 ECDOTICA - ANALIZADOR AUTOMÁTICO DE LIBROS")
    print("="*60 + "\n")
    
    # 1. Crear carpetas
    crear_carpetas()
    
    # 2. Buscar libros
    libros = listar_libros()
    
    if not libros:
        print("⚠️  No se encontraron libros en la carpeta 'uploads/'")
        print("\n📁 Cómo agregar libros:")
        print("   1. Copia tus archivos PDF o DOCX a la carpeta 'uploads/'")
        print("   2. Ejecuta este script nuevamente")
        print("\nEjemplo:")
        print("   cp mi_libro.pdf uploads/")
        print("   python analizar_libros_simple.py")
        return
    
    print(f"📚 Libros encontrados: {len(libros)}\n")
    for libro in libros:
        print(f"   - {libro.name}")
    
    print("\n" + "-"*60)
    respuesta = input("\n❓ ¿Deseas analizar estos libros? (s/n): ")
    
    if respuesta.lower() not in ['s', 'si', 'sí', 'yes', 'y']:
        print("\n❌ Análisis cancelado")
        return
    
    # 3. Inicializar procesador
    print("\n🚀 Iniciando procesamiento...\n")
    processor = BookProcessor(
        upload_dir="uploads",
        reports_dir="reports"
    )
    
    # 4. Procesar cada libro
    resultados = []
    for i, libro in enumerate(libros, 1):
        print(f"\n[{i}/{len(libros)}] Procesando: {libro.name}")
        print("-" * 40)
        
        try:
            resultado = await processor.procesar_libro(
                file_path=libro,
                titulo=libro.stem
            )
            
            if resultado['status'] == 'success':
                print(f"✅ Éxito!")
                print(f"   📄 Caracteres: {resultado['metadata']['num_caracteres']:,}")
                print(f"   📖 Palabras: {resultado['metadata']['num_palabras']:,}")
                print(f"   📊 Reporte: {Path(resultado['reporte_path']).name}")
            else:
                print(f"❌ Error: {resultado.get('error', 'Desconocido')}")
            
            resultados.append(resultado)
            
        except Exception as e:
            print(f"❌ Error procesando {libro.name}: {e}")
            resultados.append({
                'status': 'error',
                'file': str(libro),
                'error': str(e)
            })
    
    # 5. Resumen final
    print("\n" + "="*60)
    print("🎯 RESUMEN DEL PROCESAMIENTO")
    print("="*60 + "\n")
    
    exitosos = sum(1 for r in resultados if r['status'] == 'success')
    errores = len(resultados) - exitosos
    
    print(f"✅ Procesados exitosamente: {exitosos}")
    print(f"❌ Con errores: {errores}")
    print(f"\n📂 Los reportes están en: reports/")
    
    # Listar reportes generados
    reports_dir = Path("reports")
    reportes = list(reports_dir.glob("*.md"))
    if reportes:
        print("\n📊 Reportes generados:")
        for reporte in reportes:
            print(f"   - {reporte.name}")
    
    print("\n✨ ¡Proceso completado!\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        print("\n🐞 Si el error persiste, verifica:")
        print("   1. Dependencias instaladas: pip install -r requirements/base.txt")
        print("   2. Modelo SpaCy: python -m spacy download es_core_news_sm")
