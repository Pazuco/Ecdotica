"""
Servicio de Procesamiento Automático de Libros
Procesa PDF y DOCX, extrae texto, analiza con NLP y genera reportes
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

from PyPDF2 import PdfReader
import docx
import spacy
from loguru import logger

# Importar desde src (módulos existentes)
from src.procesamiento.archivos import ProcesadorDeArchivos
from src.procesamiento.nlp import analizar_texto_completo


class BookProcessor:
    """
    Procesador de libros con análisis NLP automático
    """
    
    def __init__(self, upload_dir: str = "uploads", reports_dir: str = "reports"):
        self.upload_dir = Path(upload_dir)
        self.reports_dir = Path(reports_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Cargar modelo SpaCy
        try:
            self.nlp = spacy.load("es_core_news_sm")
            logger.info("Modelo SpaCy cargado correctamente")
        except OSError:
            logger.warning("Modelo SpaCy no encontrado, usar: python -m spacy download es_core_news_sm")
            self.nlp = None
    
    def calcular_hash(self, file_path: Path) -> str:
        """Calcular hash SHA256 del archivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()[:16]
    
    def extraer_texto_pdf(self, file_path: Path) -> str:
        """Extraer texto de PDF"""
        try:
            reader = PdfReader(str(file_path))
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() + "\n"
            return texto.strip()
        except Exception as e:
            logger.error(f"Error extrayendo PDF: {e}")
            return ""
    
    def extraer_texto_docx(self, file_path: Path) -> str:
        """Extraer texto de DOCX"""
        try:
            doc = docx.Document(str(file_path))
            texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            return texto.strip()
        except Exception as e:
            logger.error(f"Error extrayendo DOCX: {e}")
            return ""
    
    def extraer_texto(self, file_path: Path) -> Dict:
        """Extraer texto según el formato"""
        extension = file_path.suffix.lower()
        
        if extension == ".pdf":
            texto = self.extraer_texto_pdf(file_path)
        elif extension in [".docx", ".doc"]:
            texto = self.extraer_texto_docx(file_path)
        else:
            raise ValueError(f"Formato no soportado: {extension}")
        
        return {
            "texto": texto,
            "num_caracteres": len(texto),
            "num_palabras": len(texto.split()),
            "formato": extension[1:]
        }
    
    def analizar_libro(self, texto: str) -> Dict:
        """Realizar análisis NLP completo"""
        if not self.nlp or not texto:
            return {"error": "Modelo NLP no disponible o texto vacío"}
        
        # Limitar texto para análisis (primeros 100k caracteres)
        texto_muestra = texto[:100000] if len(texto) > 100000 else texto
        
        doc = self.nlp(texto_muestra)
        
        # Estadísticas básicas
        stats = {
            "num_oraciones": len(list(doc.sents)),
            "num_tokens": len(doc),
            "num_palabras_unicas": len(set([token.text.lower() for token in doc if token.is_alpha])),
        }
        
        # Entidades nombradas
        entidades = {}
        for ent in doc.ents:
            if ent.label_ not in entidades:
                entidades[ent.label_] = []
            entidades[ent.label_].append(ent.text)
        
        stats["entidades"] = {k: list(set(v))[:10] for k, v in entidades.items()}
        
        # Sustantivos y verbos más comunes
        sustantivos = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
        verbos = [token.lemma_ for token in doc if token.pos_ == "VERB"]
        
        from collections import Counter
        stats["sustantivos_frecuentes"] = dict(Counter(sustantivos).most_common(20))
        stats["verbos_frecuentes"] = dict(Counter(verbos).most_common(20))
        
        return stats
    
    def generar_reporte(self, metadata: Dict, analisis: Dict) -> str:
        """Generar reporte en Markdown"""
        reporte = f"""# Reporte de Análisis - {metadata['titulo']}

## Metadatos

- **Archivo**: {metadata['nombre_archivo']}
- **Formato**: {metadata['formato']}
- **Fecha de análisis**: {metadata['fecha']}
- **Hash**: {metadata['hash']}

## Estadísticas del Texto

- **Caracteres**: {metadata['num_caracteres']:,}
- **Palabras**: {metadata['num_palabras']:,}
- **Oraciones**: {analisis.get('num_oraciones', 'N/A'):,}
- **Tokens**: {analisis.get('num_tokens', 'N/A'):,}
- **Palabras únicas**: {analisis.get('num_palabras_unicas', 'N/A'):,}

## Entidades Nombradas

"""
        if 'entidades' in analisis:
            for tipo, lista in analisis['entidades'].items():
                reporte += f"\n### {tipo}\n"
                reporte += ", ".join(lista[:10]) + "\n"
        
        reporte += "\n## Palabras Más Frecuentes\n\n"
        
        if 'sustantivos_frecuentes' in analisis:
            reporte += "\n### Sustantivos\n"
            for palabra, freq in list(analisis['sustantivos_frecuentes'].items())[:15]:
                reporte += f"- {palabra}: {freq}\n"
        
        if 'verbos_frecuentes' in analisis:
            reporte += "\n### Verbos\n"
            for palabra, freq in list(analisis['verbos_frecuentes'].items())[:15]:
                reporte += f"- {palabra}: {freq}\n"
        
        reporte += "\n---\n\n*Generado por Ecdotica 2.0*\n"
        return reporte
    
    async def procesar_libro(self, file_path: Path, titulo: str = None) -> Dict:
        """Proceso completo de análisis de libro"""
        logger.info(f"Iniciando procesamiento de: {file_path.name}")
        
        try:
            # 1. Extraer texto
            extraccion = self.extraer_texto(file_path)
            
            # 2. Analizar con NLP
            analisis = self.analizar_libro(extraccion['texto'])
            
            # 3. Crear metadata
            metadata = {
                "titulo": titulo or file_path.stem,
                "nombre_archivo": file_path.name,
                "formato": extraccion['formato'],
                "fecha": datetime.now().isoformat(),
                "hash": self.calcular_hash(file_path),
                "num_caracteres": extraccion['num_caracteres'],
                "num_palabras": extraccion['num_palabras']
            }
            
            # 4. Generar reporte
            reporte = self.generar_reporte(metadata, analisis)
            
            # 5. Guardar reporte
            report_filename = f"{metadata['hash']}_{file_path.stem}_report.md"
            report_path = self.reports_dir / report_filename
            report_path.write_text(reporte, encoding='utf-8')
            
            logger.success(f"Libro procesado exitosamente: {file_path.name}")
            
            return {
                "status": "success",
                "metadata": metadata,
                "analisis": analisis,
                "reporte_path": str(report_path)
            }
            
        except Exception as e:
            logger.error(f"Error procesando libro {file_path.name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "file": str(file_path)
            }
