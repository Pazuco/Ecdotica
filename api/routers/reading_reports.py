"""Router de FastAPI para el módulo de Informes de Lectura.

Endpoints para solicitar, consultar y obtener informes de lectura
generados por IA para libros y obras literarias.

Uso:
    from api.routers.reading_reports import router
    app.include_router(router)
"""

import logging

from fastapi import APIRouter, HTTPException

from api.models.reading_reports import (
    EstadoTrabajo,
    RespuestaInformeCompleto,
    RespuestaTrabajo,
    SolicitudInformeLectura,
)
from api.services.report_generator import GeneradorInformes

logger = logging.getLogger("ecdotica.informes_lectura")

router = APIRouter(
    prefix="/api/v1/informes-lectura",
    tags=["Informes de Lectura"],
    responses={
        404: {"description": "Trabajo no encontrado"},
        500: {"description": "Error interno del servidor"},
    },
)

generador = GeneradorInformes()


@router.post(
    "",
    response_model=RespuestaTrabajo,
    status_code=202,
    summary="Solicitar un informe de lectura",
    description="Crea un trabajo asíncrono para generar un informe de lectura "
    "profesional de un libro usando IA.",
)
async def crear_informe_lectura(
    solicitud: SolicitudInformeLectura,
) -> RespuestaTrabajo:
    """Crea una solicitud de informe de lectura y devuelve el ID del trabajo."""
    try:
        trabajo_id = await generador.crear_trabajo(solicitud)
        estado = generador.obtener_estado(trabajo_id)
        if estado is None:
            raise HTTPException(
                status_code=500,
                detail="Error al crear el trabajo de generación",
            )
        logger.info(
            "Solicitud de informe recibida: '%s' de %s (formato: %s)",
            solicitud.titulo_libro,
            solicitud.autor,
            solicitud.formato.value,
        )
        return estado
    except Exception as e:
        logger.error("Error al crear solicitud de informe: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la solicitud: {e}",
        ) from e


@router.get(
    "/{trabajo_id}",
    response_model=RespuestaTrabajo,
    summary="Consultar estado del informe",
    description="Consulta el estado actual de un trabajo de generación de informe.",
)
async def obtener_estado_informe(trabajo_id: str) -> RespuestaTrabajo:
    """Devuelve el estado actual de un trabajo de generación de informe."""
    estado = generador.obtener_estado(trabajo_id)
    if estado is None:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró el trabajo con ID: {trabajo_id}",
        )
    return estado


@router.get(
    "/{trabajo_id}/report",
    response_model=RespuestaInformeCompleto,
    summary="Obtener informe completo",
    description="Obtiene el informe de lectura completo una vez que el trabajo "
    "ha sido completado.",
)
async def obtener_informe_completo(
    trabajo_id: str,
) -> RespuestaInformeCompleto:
    """Devuelve el informe de lectura completo si el trabajo ha finalizado."""
    estado = generador.obtener_estado(trabajo_id)
    if estado is None:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró el trabajo con ID: {trabajo_id}",
        )
    if estado.estado == EstadoTrabajo.FALLIDO:
        raise HTTPException(
            status_code=422,
            detail=f"El trabajo falló: {estado.mensaje}",
        )
    if estado.estado != EstadoTrabajo.COMPLETADO:
        raise HTTPException(
            status_code=409,
            detail=f"El informe aún no está listo. Estado actual: {estado.estado.value} "
            f"({estado.progreso}%)",
        )

    informe = generador.obtener_informe(trabajo_id)
    if informe is None:
        raise HTTPException(
            status_code=500,
            detail="Error al recuperar el informe generado",
        )
    return informe
