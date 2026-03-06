"""
Ecdotica 2.0 - FastAPI Backend Principal
Editor de texto especializado en edición crítica digital
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
