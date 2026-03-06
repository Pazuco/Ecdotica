"""
Modelo SQLAlchemy para Documento
Representa un documento editorial en Ecdotica
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

# Base se importaría desde database.py
# from backend.database import Base


class TipoGenero(str, enum.Enum):
    """Géneros literarios soportados"""
    NARRATIVA = "narrativa"
    LIRICA = "lirica"
    DRAMA = "drama"
    ENSAYO = "ensayo"
    CRONICA = "cronica"
    CRITICA = "critica"


class EstadoDocumento(str, enum.Enum):
    """Estados del flujo editorial"""
    BORRADOR = "borrador"
    REVISION = "revision"
    EDICION = "edicion"
    APROBADO = "aprobado"
    PUBLICADO = "publicado"


# class Documento(Base):
class Documento:
    """Modelo principal de Documento"""
    
    # __tablename__ = "documentos"
    
    # Identificación
    # id = Column(Integer, primary_key=True, index=True)
    # titulo = Column(String(500), nullable=False, index=True)
    # subtitulo = Column(String(500), nullable=True)
    
    # Contenido
    # contenido = Column(Text, nullable=False)
    # contenido_tei_xml = Column(Text, nullable=True)  # Versión TEI-XML
    
    # Metadatos editoriales
    # autor = Column(String(200), nullable=False, index=True)
    # genero = Column(Enum(TipoGenero), nullable=False, index=True)
    # estado = Column(Enum(EstadoDocumento), default=EstadoDocumento.BORRADOR)
    
    # Estadísticas NLP
    # num_palabras = Column(Integer, default=0)
    # num_caracteres = Column(Integer, default=0)
    # idioma = Column(String(10), default="es")
    
    # Control de versiones
    # version = Column(Integer, default=1)
    # es_variante = Column(Boolean, default=False)
    # documento_original_id = Column(Integer, ForeignKey("documentos.id"), nullable=True)
    
    # Timestamps
    # creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    # actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # publicado_en = Column(DateTime, nullable=True)
    
    # Relaciones
    # variantes = relationship("Documento", backref="original", remote_side=[id])
    # anotaciones = relationship("Anotacion", back_populates="documento")
    
    def __repr__(self):
        return f"<Documento(id={self.id}, titulo='{self.titulo}', autor='{self.autor}')>"
    
    @property
    def resumen_estadisticas(self):
        """Resumen de estadísticas del documento"""
        return {
            "palabras": self.num_palabras,
            "caracteres": self.num_caracteres,
            "version": self.version,
            "idioma": self.idioma
        }
