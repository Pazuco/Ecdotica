# Cloudflare Workers — Ecdótica

## Workers activos

| Worker | Archivo | Config | Ruta | Deploy |
|--------|---------|--------|------|--------|
| ecdotica-adsense | `ecdotica-adsense.js` | `wrangler.ecdotica-adsense.toml` | `ecdotica.com/*` | CI automático (push a main) |
| ecdotica-analyzer | Conectado directo al repo | — | `ecdotica.com/analyzer*` | CI automático |
| ecdoticon | `ecdoticon.js` | `wrangler.ecdoticon.toml` | `ecdotica.com/api/ecdoticon` | Manual |
| ecdotica-api | `index.js` | `wrangler.toml` | Solo workers.dev | Manual |

## Workers eliminados

- ~~ecdotica-plagiarism-checker~~ — Eliminado el 5 marzo 2026 (API keys expuestas, sin rutas activas)

## Deploy manual

```bash
npx wrangler deploy --config wrangler.ecdoticon.toml
npx wrangler deploy --config wrangler.toml
```

## Notas

- **api.ecdotica.com** apunta a Railway (CNAME → sweet-luck-production.up.railway.app), NO a un Worker
- El Worker ecdotica-adsense sirve ads.txt y pasa el resto al origen (WordPress en EasyWP)
- Variables sensibles (API keys) se configuran como secrets en Cloudflare: `wrangler secret put NOMBRE_VARIABLE`
