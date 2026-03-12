# Informes de Lectura — Documentación

## Descripción General

**Informes de Lectura** es un módulo de Ecdótica que genera reseñas y análisis literarios profesionales utilizando inteligencia artificial (GPT-4). Los usuarios pueden solicitar informes de lectura para cualquier libro, recibiendo un análisis estructurado con calidad de crítica literaria.

## Arquitectura

```
┌─────────────────────┐     ┌──────────────────────────────┐
│  WordPress Frontend  │────▶│  FastAPI Backend (Railway)    │
│  informes-lectura    │◀────│  /api/v1/informes-lectura    │
│  .html               │     │                              │
└─────────────────────┘     │  ┌─────────────────────────┐ │
                            │  │  Router (endpoints)      │ │
                            │  └──────────┬──────────────┘ │
                            │             │                 │
                            │  ┌──────────▼──────────────┐ │
                            │  │  GeneradorInformes       │ │
                            │  │  (servicio + job store)  │ │
                            │  └──────────┬──────────────┘ │
                            │             │                 │
                            │  ┌──────────▼──────────────┐ │
                            │  │  OpenAI API (GPT-4)      │ │
                            │  │  Prompts especializados  │ │
                            │  └──────────────────────────┘ │
                            └──────────────────────────────┘
```

### Componentes

| Componente | Archivo | Responsabilidad |
|---|---|---|
| Modelos | `api/models/reading_reports.py` | Validación de datos con Pydantic |
| Prompts | `api/prompts/reading_reports.py` | Plantillas de prompts para GPT-4 |
| Servicio | `api/services/report_generator.py` | Lógica de negocio y generación async |
| Router | `api/routers/reading_reports.py` | Endpoints HTTP de FastAPI |
| Frontend | `wordpress/informes-lectura.html` | Interfaz de usuario embebible en WordPress |

### Flujo de Datos

1. El usuario completa el formulario en WordPress
2. JavaScript envía un `POST` a `/api/v1/informes-lectura`
3. El backend crea un trabajo asíncrono y devuelve `trabajo_id`
4. El frontend hace polling con `GET /{trabajo_id}` cada 3 segundos
5. Cuando el estado es `completado`, solicita el informe con `GET /{trabajo_id}/report`
6. El informe se renderiza en la página

## Endpoints de la API

### `POST /api/v1/informes-lectura`

Crea una solicitud de informe de lectura.

**Request Body:**

```json
{
    "titulo_libro": "Cien años de soledad",
    "autor": "Gabriel García Márquez",
    "genero": "Novela",
    "notas_usuario": "Enfoque en el realismo mágico y la estructura temporal",
    "formato": "estandar",
    "email_usuario": "lector@ejemplo.com"
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `titulo_libro` | string | Sí | Título del libro (1-500 caracteres) |
| `autor` | string | Sí | Nombre del autor (1-300 caracteres) |
| `genero` | string | No | Género literario |
| `notas_usuario` | string | No | Áreas de enfoque (máx. 2000 caracteres) |
| `formato` | string | No | `breve`, `estandar` (default), `detallado` |
| `email_usuario` | email | Sí | Correo del usuario |

**Response (202 Accepted):**

```json
{
    "trabajo_id": "550e8400-e29b-41d4-a716-446655440000",
    "estado": "pendiente",
    "progreso": 0,
    "mensaje": "Trabajo creado, en cola de procesamiento",
    "fecha_creacion": "2026-03-12T15:30:00.000Z",
    "fecha_completado": null
}
```

### `GET /api/v1/informes-lectura/{trabajo_id}`

Consulta el estado de un trabajo.

**Response (200 OK):**

```json
{
    "trabajo_id": "550e8400-e29b-41d4-a716-446655440000",
    "estado": "procesando",
    "progreso": 50,
    "mensaje": "Generando informe de lectura con IA...",
    "fecha_creacion": "2026-03-12T15:30:00.000Z",
    "fecha_completado": null
}
```

**Estados posibles:** `pendiente`, `procesando`, `completado`, `fallido`

### `GET /api/v1/informes-lectura/{trabajo_id}/report`

Obtiene el informe completo (solo disponible cuando `estado` es `completado`).

**Response (200 OK):**

```json
{
    "trabajo_id": "550e8400-e29b-41d4-a716-446655440000",
    "estado": "completado",
    "informe": {
        "ficha_bibliografica": {
            "titulo": "Cien años de soledad",
            "autor": "Gabriel García Márquez",
            "genero": "Novela",
            "anio_publicacion": "1967",
            "editorial": "Editorial Sudamericana",
            "idioma": "Español",
            "paginas_estimadas": "471"
        },
        "sinopsis": "La historia de siete generaciones de la familia Buendía...",
        "analisis_tematico": "Los temas centrales de la novela incluyen...",
        "analisis_estilo_estructura": "García Márquez emplea un estilo...",
        "contexto_literario": "Publicada en 1967, en pleno auge del Boom...",
        "valoracion_critica": "Cien años de soledad es considerada...",
        "publico_recomendado": "Esta obra es ideal para...",
        "calificacion": 5,
        "justificacion_calificacion": "Una obra maestra indiscutible..."
    },
    "formato_solicitado": "estandar",
    "fecha_generacion": "2026-03-12T15:31:15.000Z",
    "metadata": {
        "modelo_ia": "gpt-4",
        "tokens_prompt": 450,
        "tokens_respuesta": 1800,
        "tokens_total": 2250,
        "version_api": "1.0.0"
    }
}
```

**Errores:**

| Código | Condición |
|---|---|
| 404 | Trabajo no encontrado |
| 409 | Informe aún no completado |
| 422 | Trabajo falló durante la generación |

## Integración con WordPress

### Opción 1: Bloque HTML personalizado

1. En el editor de WordPress, agregar un bloque "HTML personalizado"
2. Pegar el contenido completo de `wordpress/informes-lectura.html`
3. Publicar la página

### Opción 2: Página de plantilla

1. Subir `informes-lectura.html` al servidor de WordPress
2. Crear una página en WordPress que redirija a este archivo
3. O usar un plugin de redirección para servir la página directamente

### Consideraciones CORS

El frontend hace peticiones a `https://api.ecdotica.com`. El backend debe tener CORS configurado para permitir peticiones desde `https://ecdotica.com`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ecdotica.com", "https://www.ecdotica.com"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)
```

## Integración con la App FastAPI Existente

Agregar el router al archivo principal de la aplicación FastAPI en Railway:

```python
from api.routers.reading_reports import router as informes_lectura_router

app.include_router(informes_lectura_router)
```

## Formatos de Informe

| Formato | Longitud | Uso recomendado |
|---|---|---|
| `breve` | ~500 palabras | Vista rápida, decisión de compra |
| `estandar` | ~1500 palabras | Análisis completo para lectores |
| `detallado` | ~3000+ palabras | Estudio académico, uso editorial |

## Variables de Entorno

| Variable | Requerida | Descripción | Default |
|---|---|---|---|
| `OPENAI_API_KEY` | Sí | Clave de API de OpenAI | — |
| `OPENAI_MODEL` | No | Modelo de OpenAI a usar | `gpt-4` |

## Checklist de Despliegue en Railway

- [ ] Verificar que `OPENAI_API_KEY` está configurada en Railway
- [ ] Verificar que `OPENAI_MODEL` está configurada (opcional, default `gpt-4`)
- [ ] Agregar las dependencias al `requirements.txt` de Railway:
  - `openai>=1.0.0`
  - `pydantic[email]>=2.0.0`
  - `fastapi>=0.100.0`
- [ ] Montar el router en la app principal: `app.include_router(informes_lectura_router)`
- [ ] Verificar configuración de CORS para `ecdotica.com`
- [ ] Probar el endpoint con curl:
  ```bash
  curl -X POST https://api.ecdotica.com/api/v1/informes-lectura \
    -H "Content-Type: application/json" \
    -d '{"titulo_libro":"Rayuela","autor":"Julio Cortázar","email_usuario":"test@ecdotica.com"}'
  ```
- [ ] Subir `wordpress/informes-lectura.html` a WordPress
- [ ] Probar flujo completo desde la página de WordPress

## Ejecución de Tests

```bash
# Instalar dependencias de test
pip install pytest fastapi httpx pydantic[email] openai

# Ejecutar tests
pytest tests/test_reading_reports.py -v
```

## Planes de Precios

| Plan | Precio | Incluye |
|---|---|---|
| Plan Básico | Gratis | 1 informe breve de prueba |
| Plan Autor | $4.99/informe | Informes estándar o detallados |
| Plan Editorial | $29.99/mes | Informes ilimitados en todos los formatos |

> **Nota:** La lógica de pagos y suscripciones no está incluida en este MVP. Se integrará con Stripe/PayPal en una fase posterior.
