# Plugin WordPress — Ecdótica AI Assistant

## Estado

Plugin personalizado instalado en ecdotica.com (WordPress/WooCommerce).

## Archivos a extraer desde wp-admin

El plugin se encuentra en: `wp-content/plugins/ecdotica-ai-assistant/`

### Archivos principales:
- `ecdotica-ai-assistant.php` — Archivo principal del plugin
- `admin-page.php` — Página de administración con UI del analyzer
- `config.php` — Configuración (API endpoint, keys)
- `database-setup.php` — Schema de base de datos

### Funcionalidades:
- Detector de plagio (conecta con api.ecdotica.com)
- Análisis de manuscritos con IA (GPT-4o vía Railway)
- Panel "Ecdotica Analyzer" en sidebar de Gutenberg
- Integración con WooCommerce para suscripciones

## Para extraer el código:
1. WordPress → Plugins → Editor de plugins
2. Seleccionar "Ecdotica AI Assistant"
3. Copiar cada archivo PHP aquí
4. Commit y push

## Endpoints que consume:
- `POST https://api.ecdotica.com/api/v1/text/analyze`
- `POST https://api.ecdotica.com/api/v1/manuscripts/check-plagiarism`
- `POST https://api.ecdotica.com/api/v1/analyze`
- `GET https://api.ecdotica.com/api/v1/reports/{id}`
