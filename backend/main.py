"""
Ecdotica 2.0 - FastAPI Backend Principal
Editor de texto especializado en edición crítica digital
"""

import sys
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from loguru import logger

# Agregar src al path para importar el pipeline de análisis
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configurar logging
logger.add("logs/ecdotica.log", rotation="500 MB")

# Crear aplicación FastAPI
app = FastAPI(
    title="Ecdotica API",
    description="API REST para Ecdotica 2.0 - Editor de Edición Crítica Digital",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    logger.info("Iniciando Ecdotica 2.0 API...")
    # Aquí se inicializarían conexiones a BD, cache, etc.


@app.on_event("shutdown")
async def shutdown_event():
    """Eventos al cerrar la aplicación"""
    logger.info("Cerrando Ecdotica 2.0 API...")
    # Aquí se cerrarían conexiones


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Ecdotica 2.0 API",
        "version": "2.0.0",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check para Docker y monitoreo"""
    return {
        "status": "healthy",
        "service": "ecdotica-api"
    }


@app.get("/api/v1/info")
async def api_info():
    """Información de la API"""
    return {
        "name": "Ecdotica",
        "version": "2.0.0",
        "description": "Primer editor open source especializado en edición crítica digital",
        "features": [
            "Análisis NLP avanzado",
            "Colaboración en tiempo real",
            "Exportación TEI-XML, PDF, HTML",
            "Búsqueda semántica",
            "Editor inteligente"
        ]
    }


class SolicitudAnalisis(BaseModel):
    texto: str
    genero: str


@app.post("/api/v1/analizar")
async def analizar_manuscrito(solicitud: SolicitudAnalisis):
    """
    Analiza un manuscrito según el género indicado y devuelve estadísticas
    y resultados de evaluación editorial.

    Géneros válidos: novela, cuento, poema, ensayo, cronica
    """
    generos_validos = {'novela', 'cuento', 'poema', 'ensayo', 'cronica'}
    if solicitud.genero not in generos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Género no válido: '{solicitud.genero}'. Válidos: {sorted(generos_validos)}"
        )

    if len(solicitud.texto.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="El texto debe tener al menos 50 caracteres."
        )

    try:
        from procesamiento.utils import (
            contar_palabras,
            contar_capitulos,
            calcular_legibilidad,
            detectar_errores,
        )
        from procesamiento.evaluador import evaluar_manuscrito

        stats = {
            'num_palabras': contar_palabras(solicitud.texto),
            'num_capitulos': contar_capitulos(solicitud.texto),
            'indice_legibilidad': calcular_legibilidad(solicitud.texto),
            'errores_graves': detectar_errores(solicitud.texto),
        }

        resultados = evaluar_manuscrito(stats, solicitud.genero)

        return {
            "status": "ok",
            "genero": solicitud.genero,
            "stats": stats,
            "resultados": resultados,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en análisis de manuscrito: {e}")
        raise HTTPException(status_code=500, detail="Error interno durante el análisis.")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
