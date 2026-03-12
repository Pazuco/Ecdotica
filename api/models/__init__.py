"""Modelos Pydantic para la API de Ecdótica."""

from .reading_reports import (
    FormatoInforme,
    SolicitudInformeLectura,
    EstadoTrabajo,
    RespuestaTrabajo,
    FichaBibliografica,
    SeccionInforme,
    InformeLecturaCompleto,
    RespuestaInformeCompleto,
)

__all__ = [
    "FormatoInforme",
    "SolicitudInformeLectura",
    "EstadoTrabajo",
    "RespuestaTrabajo",
    "FichaBibliografica",
    "SeccionInforme",
    "InformeLecturaCompleto",
    "RespuestaInformeCompleto",
]
