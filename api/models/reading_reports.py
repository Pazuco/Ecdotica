"""Modelos Pydantic para el módulo de Informes de Lectura.

Define las estructuras de datos para solicitudes, respuestas,
y el contenido completo de los informes de lectura generados por IA.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class FormatoInforme(str, Enum):
    """Formatos disponibles para los informes de lectura."""

    BREVE = "breve"
    ESTANDAR = "estandar"
    DETALLADO = "detallado"


class SolicitudInformeLectura(BaseModel):
    """Solicitud para generar un informe de lectura."""

    titulo_libro: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Título del libro a analizar",
    )
    autor: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Nombre del autor o autores",
    )
    genero: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Género literario (novela, cuento, poesía, ensayo, etc.)",
    )
    notas_usuario: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notas o áreas de enfoque del usuario para el informe",
    )
    formato: FormatoInforme = Field(
        default=FormatoInforme.ESTANDAR,
        description="Formato del informe: breve (~500 palabras), estándar (~1500 palabras), detallado (~3000+ palabras)",
    )
    email_usuario: EmailStr = Field(
        ...,
        description="Correo electrónico del usuario para entrega del informe",
    )

    @field_validator("titulo_libro", "autor")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        """Valida que los campos de texto no estén vacíos tras eliminar espacios."""
        v = v.strip()
        if not v:
            raise ValueError("El campo no puede estar vacío")
        return v


class EstadoTrabajo(str, Enum):
    """Estados posibles de un trabajo de generación de informe."""

    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    FALLIDO = "fallido"


class RespuestaTrabajo(BaseModel):
    """Respuesta con el estado de un trabajo de generación de informe."""

    trabajo_id: str = Field(..., description="Identificador único del trabajo")
    estado: EstadoTrabajo = Field(..., description="Estado actual del trabajo")
    progreso: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Porcentaje de progreso (0-100)",
    )
    mensaje: Optional[str] = Field(
        default=None,
        description="Mensaje descriptivo del estado actual",
    )
    fecha_creacion: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Fecha y hora de creación del trabajo",
    )
    fecha_completado: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora de finalización del trabajo",
    )


class FichaBibliografica(BaseModel):
    """Ficha bibliográfica del libro analizado."""

    titulo: str
    autor: str
    genero: Optional[str] = None
    anio_publicacion: Optional[str] = None
    editorial: Optional[str] = None
    idioma: Optional[str] = "Español"
    paginas_estimadas: Optional[str] = None


class SeccionInforme(BaseModel):
    """Sección individual del informe de lectura."""

    titulo_seccion: str
    contenido: str


class InformeLecturaCompleto(BaseModel):
    """Informe de lectura completo generado por IA."""

    ficha_bibliografica: FichaBibliografica
    sinopsis: str = Field(..., description="Sinopsis sin spoilers")
    analisis_tematico: str = Field(..., description="Análisis de temas principales")
    analisis_estilo_estructura: str = Field(
        ..., description="Análisis de estilo y estructura narrativa"
    )
    contexto_literario: str = Field(
        ..., description="Contexto histórico/cultural e influencias"
    )
    valoracion_critica: str = Field(
        ..., description="Valoración crítica con fortalezas y debilidades"
    )
    publico_recomendado: str = Field(
        ..., description="Público objetivo recomendado"
    )
    calificacion: int = Field(
        ..., ge=1, le=5, description="Calificación de 1 a 5 estrellas"
    )
    justificacion_calificacion: str = Field(
        ..., description="Justificación de la calificación asignada"
    )


class RespuestaInformeCompleto(BaseModel):
    """Respuesta completa con el informe de lectura."""

    trabajo_id: str
    estado: EstadoTrabajo
    informe: InformeLecturaCompleto
    formato_solicitado: FormatoInforme
    fecha_generacion: datetime
    metadata: dict = Field(
        default_factory=dict,
        description="Metadatos adicionales (modelo usado, tokens, etc.)",
    )
