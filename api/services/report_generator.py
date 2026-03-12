"""Servicio de generación de Informes de Lectura.

Gestiona el almacenamiento de trabajos en memoria y la generación
asíncrona de informes mediante la API de OpenAI (GPT-4).
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import UTC, datetime
from typing import Optional

from openai import AsyncOpenAI

from api.models.reading_reports import (
    EstadoTrabajo,
    FormatoInforme,
    InformeLecturaCompleto,
    RespuestaInformeCompleto,
    RespuestaTrabajo,
    SolicitudInformeLectura,
)
from api.prompts.reading_reports import construir_prompt_informe

logger = logging.getLogger("ecdotica.informes_lectura")


class AlmacenTrabajos:
    """Almacén en memoria para trabajos de generación de informes.

    Para el MVP se usa un diccionario en memoria. En producción
    se puede reemplazar por Redis o una base de datos.
    """

    def __init__(self) -> None:
        self._trabajos: dict[str, dict] = {}

    def crear_trabajo(self, solicitud: SolicitudInformeLectura) -> str:
        """Crea un nuevo trabajo y devuelve su ID."""
        trabajo_id = str(uuid.uuid4())
        self._trabajos[trabajo_id] = {
            "solicitud": solicitud,
            "estado": EstadoTrabajo.PENDIENTE,
            "progreso": 0,
            "mensaje": "Trabajo creado, en cola de procesamiento",
            "fecha_creacion": datetime.now(UTC),
            "fecha_completado": None,
            "informe": None,
            "metadata": {},
        }
        return trabajo_id

    def obtener_trabajo(self, trabajo_id: str) -> Optional[dict]:
        """Obtiene los datos de un trabajo por su ID."""
        return self._trabajos.get(trabajo_id)

    def actualizar_estado(
        self,
        trabajo_id: str,
        estado: EstadoTrabajo,
        progreso: int = 0,
        mensaje: str = "",
    ) -> None:
        """Actualiza el estado de un trabajo existente."""
        if trabajo_id in self._trabajos:
            self._trabajos[trabajo_id]["estado"] = estado
            self._trabajos[trabajo_id]["progreso"] = progreso
            self._trabajos[trabajo_id]["mensaje"] = mensaje

    def guardar_informe(
        self,
        trabajo_id: str,
        informe: InformeLecturaCompleto,
        metadata: dict,
    ) -> None:
        """Guarda el informe generado en el trabajo correspondiente."""
        if trabajo_id in self._trabajos:
            self._trabajos[trabajo_id]["informe"] = informe
            self._trabajos[trabajo_id]["metadata"] = metadata
            self._trabajos[trabajo_id]["estado"] = EstadoTrabajo.COMPLETADO
            self._trabajos[trabajo_id]["progreso"] = 100
            self._trabajos[trabajo_id]["mensaje"] = "Informe generado exitosamente"
            self._trabajos[trabajo_id]["fecha_completado"] = datetime.now(UTC)

    def marcar_fallido(self, trabajo_id: str, mensaje_error: str) -> None:
        """Marca un trabajo como fallido con un mensaje de error."""
        if trabajo_id in self._trabajos:
            self._trabajos[trabajo_id]["estado"] = EstadoTrabajo.FALLIDO
            self._trabajos[trabajo_id]["mensaje"] = mensaje_error
            self._trabajos[trabajo_id]["fecha_completado"] = datetime.now(UTC)


# Instancia global del almacén de trabajos
almacen_trabajos = AlmacenTrabajos()


class GeneradorInformes:
    """Servicio principal para generar informes de lectura con IA."""

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning(
                "OPENAI_API_KEY no configurada. "
                "La generación de informes no estará disponible."
            )
        self._cliente = AsyncOpenAI(api_key=api_key) if api_key else None
        self._modelo = os.getenv("OPENAI_MODEL", "gpt-4")

    async def crear_trabajo(self, solicitud: SolicitudInformeLectura) -> str:
        """Crea un trabajo de generación y lanza el procesamiento en segundo plano."""
        trabajo_id = almacen_trabajos.crear_trabajo(solicitud)
        logger.info(
            "Trabajo %s creado para '%s' de %s",
            trabajo_id,
            solicitud.titulo_libro,
            solicitud.autor,
        )
        asyncio.create_task(self._procesar_informe(trabajo_id, solicitud))
        return trabajo_id

    def obtener_estado(self, trabajo_id: str) -> Optional[RespuestaTrabajo]:
        """Obtiene el estado actual de un trabajo."""
        trabajo = almacen_trabajos.obtener_trabajo(trabajo_id)
        if trabajo is None:
            return None
        return RespuestaTrabajo(
            trabajo_id=trabajo_id,
            estado=trabajo["estado"],
            progreso=trabajo["progreso"],
            mensaje=trabajo["mensaje"],
            fecha_creacion=trabajo["fecha_creacion"],
            fecha_completado=trabajo["fecha_completado"],
        )

    def obtener_informe(
        self, trabajo_id: str
    ) -> Optional[RespuestaInformeCompleto]:
        """Obtiene el informe completo de un trabajo finalizado."""
        trabajo = almacen_trabajos.obtener_trabajo(trabajo_id)
        if trabajo is None:
            return None
        if trabajo["estado"] != EstadoTrabajo.COMPLETADO:
            return None
        if trabajo["informe"] is None:
            return None

        solicitud: SolicitudInformeLectura = trabajo["solicitud"]
        return RespuestaInformeCompleto(
            trabajo_id=trabajo_id,
            estado=trabajo["estado"],
            informe=trabajo["informe"],
            formato_solicitado=solicitud.formato,
            fecha_generacion=trabajo["fecha_completado"],
            metadata=trabajo["metadata"],
        )

    async def _procesar_informe(
        self,
        trabajo_id: str,
        solicitud: SolicitudInformeLectura,
    ) -> None:
        """Proceso asíncrono de generación del informe con OpenAI."""
        try:
            almacen_trabajos.actualizar_estado(
                trabajo_id,
                EstadoTrabajo.PROCESANDO,
                progreso=10,
                mensaje="Preparando análisis del libro...",
            )

            if self._cliente is None:
                raise RuntimeError(
                    "OPENAI_API_KEY no configurada. "
                    "No se puede generar el informe."
                )

            # Construir prompts
            prompt_sistema, prompt_usuario = construir_prompt_informe(
                titulo=solicitud.titulo_libro,
                autor=solicitud.autor,
                genero=solicitud.genero,
                notas_usuario=solicitud.notas_usuario,
                formato=solicitud.formato,
            )

            almacen_trabajos.actualizar_estado(
                trabajo_id,
                EstadoTrabajo.PROCESANDO,
                progreso=30,
                mensaje="Generando informe de lectura con IA...",
            )

            # Llamada a la API de OpenAI
            respuesta = await self._cliente.chat.completions.create(
                model=self._modelo,
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario},
                ],
                temperature=0.7,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )

            almacen_trabajos.actualizar_estado(
                trabajo_id,
                EstadoTrabajo.PROCESANDO,
                progreso=80,
                mensaje="Procesando respuesta...",
            )

            # Parsear la respuesta JSON
            contenido_json = respuesta.choices[0].message.content
            if contenido_json is None:
                raise ValueError("La respuesta de OpenAI está vacía")

            datos_informe = json.loads(contenido_json)

            # Construir el modelo del informe
            informe = InformeLecturaCompleto(**datos_informe)

            metadata = {
                "modelo_ia": self._modelo,
                "tokens_prompt": respuesta.usage.prompt_tokens if respuesta.usage else 0,
                "tokens_respuesta": respuesta.usage.completion_tokens if respuesta.usage else 0,
                "tokens_total": respuesta.usage.total_tokens if respuesta.usage else 0,
                "version_api": "1.0.0",
            }

            almacen_trabajos.guardar_informe(trabajo_id, informe, metadata)

            logger.info(
                "Informe %s generado exitosamente para '%s'",
                trabajo_id,
                solicitud.titulo_libro,
            )

        except json.JSONDecodeError as e:
            mensaje_error = f"Error al parsear la respuesta de IA: {e}"
            logger.error("Trabajo %s fallido: %s", trabajo_id, mensaje_error)
            almacen_trabajos.marcar_fallido(trabajo_id, mensaje_error)

        except Exception as e:
            mensaje_error = f"Error durante la generación del informe: {e}"
            logger.error("Trabajo %s fallido: %s", trabajo_id, mensaje_error)
            almacen_trabajos.marcar_fallido(trabajo_id, mensaje_error)
