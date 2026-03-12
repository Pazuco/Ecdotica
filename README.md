# Ecdótica — Plataforma Editorial Digital

Ecdótica es una librería digital y plataforma de herramientas editoriales para autores, editores y editoriales.

**Sitio:** [ecdotica.com](https://ecdotica.com)

## Arquitectura

```
ecdotica.com (WordPress/WooCommerce en EasyWP)
    ├── Cloudflare CDN + Workers
    │   ├── ecdotica-adsense    → ads.txt + proxy al origen
    │   ├── ecdotica-analyzer   → /analyzer*
    │   ├── ecdoticon           → /api/ecdoticon (bot literario)
    │   └── ecdotica-api        → solo workers.dev (cache/proxy)
    │
    └── api.ecdotica.com (Railway → FastAPI)
        ├── Detector de plagio (Brave Search API)
        ├── Análisis de manuscritos (GPT-4o)
        ├── Sistema de reportes v1.2
        └── Blockchain de registros
```

## Estructura del repositorio

```
├── api/                    # Módulos de la API FastAPI (Railway)
│   ├── models/            # Modelos Pydantic
│   ├── prompts/           # Prompts de IA
│   ├── routers/           # Routers/endpoints FastAPI
│   └── services/          # Lógica de negocio
├── src/                    # Analizador de manuscritos (Python)
│   ├── cuento/            # Reglas por género literario
│   ├── novela/
│   ├── poema/
│   ├── ensayo/
│   ├── cronica/
│   └── procesamiento/     # Pipeline de evaluación
├── worker/                 # Cloudflare Workers (JavaScript)
│   ├── ecdotica-adsense.js
│   ├── ecdoticon.js
│   └── index.js           # ecdotica-api
├── wordpress/              # Páginas web embebibles en WordPress
├── wordpress-plugin/       # Plugin WP "Ecdotica AI Assistant"
├── tests/                  # Tests unitarios
├── docs/                   # Documentación de módulos
├── wrangler.toml          # Config Worker ecdotica-api
├── wrangler.ecdotica-adsense.toml
├── wrangler.ecdoticon.toml
├── main.py                # Entry point del analizador
└── requirements.txt
```

## Servicios externos

| Servicio | Uso | Credenciales |
|----------|-----|-------------|
| Railway | Backend FastAPI (api.ecdotica.com) | DATABASE_URL, OPENAI_API_KEY, BRAVE_API_KEY |
| Cloudflare | CDN, DNS, Workers | Secrets por Worker |
| Stripe | Pagos de suscripciones | Configurado en WooCommerce |
| PayPal | Pagos alternativos | Configurado en WooCommerce |
| Brave Search | Detector de plagio | BRAVE_API_KEY en Railway |
| Google AdSense | Monetización (pub-7917471830627014) | Via Worker ecdotica-adsense |

## Deploy

### Workers de Cloudflare
```bash
# ecdotica-adsense y ecdotica-analyzer: CI automático al pushear a main
# ecdoticon y ecdotica-api: deploy manual:
npx wrangler deploy --config wrangler.ecdoticon.toml
npx wrangler deploy --config wrangler.toml
```

### Railway (backend API)
Autodeploy desde commits al repo en Railway.

## Informes de Lectura (Nuevo)

Módulo de generación de reseñas y análisis literarios profesionales con IA. Permite a usuarios solicitar informes de lectura estructurados para cualquier libro.

- **API:** `POST /api/v1/informes-lectura` — Solicitar informe (async)
- **API:** `GET /api/v1/informes-lectura/{id}` — Consultar estado
- **API:** `GET /api/v1/informes-lectura/{id}/report` — Obtener informe completo
- **Frontend:** `wordpress/informes-lectura.html` — Página embebible en WordPress

Documentación completa: [`docs/INFORMES_DE_LECTURA.md`](docs/INFORMES_DE_LECTURA.md)

## Licencia

MIT
