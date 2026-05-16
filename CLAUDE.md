# CLAUDE.md — Ecdotica

AI assistant reference for the Ecdotica codebase. Keep this file up to date as the project evolves.

---

## Project Overview

**Ecdotica** is a Spanish-language literary platform for **Editorial Nuevo Milenio** (Bolivian publishing house). It combines:

1. A **Python manuscript analyzer** that applies digital ecdotics — the science of text transmission and critical editing — to automate the review of submissions by literary genre.
2. **Cloudflare Workers** that power the public site (`ecdotica.com`): an in-browser manuscript analyzer + plagiarism detector, a literary chatbot (`Ecdoticón`), and an `ads.txt` shim.
3. A **WordPress plugin** that wires the editorial workflow into the WP/WooCommerce site, calling out to a separately deployed FastAPI backend on Railway (`api.ecdotica.com`).

- **Languages:** Python 3.x (analyzer + tests), JavaScript (Cloudflare Workers), PHP (WordPress plugin)
- **License:** MIT (Copyright 2025 Pazuco)
- **Domain:** Natural language processing, literary analysis, editorial automation
- **Codebase language convention:** Spanish (variable/function names, docstrings, comments, user-facing output, commit messages)

---

## High-level Architecture

```
ecdotica.com  (WordPress/WooCommerce on EasyWP)
    │
    ├── Cloudflare CDN + Workers
    │   ├── ecdotica-adsense    → /ads.txt + proxy to origin (WordPress)
    │   ├── ecdotica-analyzer   → /analyzer*  (linked directly to repo, no source file here)
    │   ├── ecdoticon           → /api/ecdoticon  (literary chatbot, OpenAI-backed)
    │   └── ecdotica-api        → workers.dev only (manuscript stats + plagiarism)
    │
    └── api.ecdotica.com  (Railway → FastAPI, NOT in this repo)
        ├── Plagiarism detection (Brave Search API)
        ├── Manuscript analysis (GPT-4o, RAG with LlamaIndex)
        ├── Report system v1.2
        └── Blockchain registry
```

The Python analyzer in `src/` and the FastAPI backend on Railway are **separate codebases** today, even though they share editorial logic. Workers reimplement subsets of that logic in JS for edge deployment.

---

## Repository Structure

```
Ecdotica/
├── main.py                              # CLI entry point (analyzer)
├── requirements.txt                     # Python deps
├── README.md                            # Public-facing project overview (Spanish)
├── CONTRIBUTING.md                      # Contribution guide (Spanish)
├── CLAUDE.md                            # This file
├── LICENSE                              # MIT
│
├── wrangler.toml                        # Worker: ecdotica-api  (workers.dev only)
├── wrangler.ecdoticon.toml              # Worker: ecdoticon     → ecdotica.com/api/ecdoticon
├── wrangler.ecdotica-adsense.toml       # Worker: ecdotica-adsense → ecdotica.com/*
│
├── src/
│   ├── editor.py                        # EditorDeTexto (basic correction detection)
│   ├── samples/sample.txt               # "Amor sin libertad" by Yuri Ortuño (reference)
│   ├── novela/  cuento/  poema/         # Per-genre placeholder modules (reglas.py + __init__)
│   ├── ensayo/  cronica/                #   (documentation-only stubs; logic lives in procesamiento/)
│   └── procesamiento/                   # Core analyzer pipeline
│       ├── README.md
│       ├── evaluador.py                 # Genre dispatch + report formatter
│       ├── archivos.py                  # PDF/DOCX/TXT ingestion + SpaCy/LanguageTool demos
│       ├── utils.py                     # Text stats (words, chapters, legibilidad, errors)
│       └── criterios/                   # Per-genre evaluation logic
│           ├── __init__.py              # Re-exports all five modules
│           ├── novela.py   cuento.py
│           ├── poema.py    ensayo.py    cronica.py
│
├── worker/                              # Cloudflare Workers (JS, bundled)
│   ├── README.md                        # Worker inventory + deploy notes
│   ├── index.js                         # ecdotica-api  (manuscript stats + plagiarism via Google CSE)
│   ├── ecdoticon.js                     # Literary chatbot (OpenAI + Wikipedia + Ecdotica search)
│   └── ecdotica-adsense.js              # Serves /ads.txt, passes through everything else
│
├── wordpress-plugin/
│   ├── README.md                        # Plugin extraction guide
│   └── ecdotica-ai-assistant.php        # "Ecdótica Analyzer v2" — shortcode + RAG call
│
└── tests/
    ├── conftest.py                      # Adds src/procesamiento to sys.path
    ├── test_utils.py
    └── test_criterios.py
```

---

## Component 1 — Python Analyzer (`src/`, `main.py`, `tests/`)

### Entry point — `main.py`

```bash
python main.py <ruta_manuscrito> <genero>
# géneros: novela, cuento, poema, ensayo, cronica
```

`main.py` inserts `src/procesamiento` on `sys.path`, calls `analizar_manuscrito(ruta)` → `evaluar_manuscrito(stats, genero)` → `reporte_resultados(...)`.

### `src/procesamiento/evaluador.py` — Evaluation Pipeline

Central orchestrator. Maps genres to their evaluation functions and generates text reports.

```python
GENERO_CRITERIOS = {
    'novela':  novela.evaluar_novela,
    'cuento':  cuento.evaluar_cuento,
    'poema':   poema.evaluar_poema,
    'ensayo':  ensayo.evaluar_ensayo,
    'cronica': cronica.evaluar_cronica,
}
```

**Key functions:**
- `evaluar_manuscrito(stats, genero)` — dispatches; raises `ValueError` for unknown genres.
- `reporte_resultados(resultados, genero)` — formats a checklist with `✓`/`✗` and a final `APTO`/`NO APTO` verdict.

Also runnable directly: `python src/procesamiento/evaluador.py <ruta> <genero>`.

### `src/procesamiento/utils.py` — Text Analysis Utilities

Regex-based text statistics. Standard library only.

| Function | Description |
|---|---|
| `contar_palabras(texto)` | Word count via `\w+` regex |
| `contar_capitulos(texto)` | Detects `Capítulo` at start of line (case-insensitive, accent-tolerant) |
| `calcular_legibilidad(texto)` | Flesch-Kincaid adaptation for Spanish, clamped to `[0, 100]` |
| `detectar_errores(texto)` | Calls LanguageTool (`es`); returns `0` if `language_tool_python` is not installed |
| `analizar_manuscrito(path)` | Reads a `.txt` file and returns the `stats` dict |

**Stats dict schema:**
```python
{
    'num_palabras': int,
    'num_capitulos': int,
    'indice_legibilidad': float,   # 0–100
    'errores_graves': int,
}
```

### `src/procesamiento/archivos.py` — File Processing

**`ProcesadorDeArchivos` class:**
- `extraer_texto(ruta)` — dispatches on extension (`.pdf` / `.docx` / `.txt`)
- `_extraer_pdf(ruta)` — `PyPDF2` (returns the string `"PyPDF2 no instalado"` if missing — caller should be aware this is a degraded mode, not an exception)
- `_extraer_docx(ruta)` — `python-docx` (same degradation pattern)
- `_extraer_txt(ruta)` — UTF-8 read

**Module-level NLP demos (require SpaCy + LanguageTool):**
- `analizar_texto_ejemplo()` — runs entity recognition, token analysis, sentence segmentation, and LanguageTool spell-check on `samples/sample.txt`. Demonstration only.
- `obtener_estadisticas_texto(ruta_archivo)` — returns a SpaCy-powered stats dict (characters, words, sentences, tokens, named entities).

### `src/procesamiento/criterios/` — Genre Evaluation Criteria

Each module exports a single `evaluar_<genero>(stats)` returning a dict of `{criterio_name: {cumple, mensaje, ...extra}}`. All five genres share the same four-criterion shape:

```python
{
    'ortografia_gramatica': { 'cumple': bool, 'tasa_error': float, 'mensaje': str },
    'longitud':             { 'cumple': bool, 'num_palabras': int, 'mensaje': str },
    'estructura':           { 'cumple': bool, 'mensaje': str, ... },   # capitulos para novela
    'legibilidad':          { 'cumple': bool, 'indice': float, 'mensaje': str },
}
```

**Genre criteria table:**

| Genre     | Word Range       | Chapters     | Error Threshold       | Legibility Min |
|-----------|------------------|--------------|-----------------------|----------------|
| `novela`  | 30,000–150,000   | ≥ 3 required | < 10 per 10,000 words | ≥ 50           |
| `cuento`  | 1,000–30,000     | not required | < 5 per 5,000 words   | ≥ 60           |
| `poema`   | 5–2,000          | not required | < 5 per 1,000 words   | ≥ 30           |
| `ensayo`  | 1,500–30,000     | not required | < 3 per 10,000 words  | ≥ 40           |
| `cronica` | 500–15,000       | not required | < 5 per 5,000 words   | ≥ 55           |

`criterios/__init__.py` re-exports all five modules so `from criterios import novela, cuento, poema, ensayo, cronica` works.

### `src/editor.py` — Text Editor Utilities

`EditorDeTexto` class — small helpers for double-space detection, missing terminal punctuation, and a hand-coded typo dictionary. Independent of the analyzer pipeline; not currently wired into `main.py`.

### `src/<genero>/reglas.py` — Per-Genre Placeholder Modules

`src/novela/`, `src/cuento/`, `src/poema/`, `src/ensayo/`, `src/cronica/` each contain a stub `reglas.py` (~30 lines, all-docstring) sketching genre-specific business logic to add later. **Do not confuse these with `src/procesamiento/criterios/`** — the real evaluation logic lives in `criterios/`. The `src/<genero>/` modules are documentation-only scaffolding.

### Python Dependencies (`requirements.txt`)

```
spacy>=3.0.0
language-tool-python>=2.7.0
PyPDF2>=3.0.0
python-docx>=0.8.11
pytest>=7.0.0
```

After install, fetch the Spanish SpaCy model:

```bash
python -m spacy download es_core_news_sm
```

SpaCy model options: `es_core_news_sm` (default), `es_core_news_md`, `es_core_news_lg`.

LanguageTool language code: `'es'` or `'es-ES'`.

`PyPDF2` and `python-docx` are effectively optional — `archivos.py` returns a placeholder string instead of raising if either is absent. `language_tool_python` is similarly optional in `utils.detectar_errores`.

### Tests

```bash
pytest tests/ -v
```

- `tests/conftest.py` — adds `src/procesamiento` to `sys.path`
- `tests/test_utils.py` — covers `contar_palabras`, `contar_capitulos`, `calcular_legibilidad`, `analizar_manuscrito`
- `tests/test_criterios.py` — class-per-genre; one `TestNovela`, `TestCuento`, `TestPoema`, `TestEnsayo`, `TestCronica` with fixtures for `stats_<genero>_apt[oa]`

When adding genres or functions, follow the class-per-module pattern and reuse the `stats_<genero>_apt[oa]` fixture style.

---

## Component 2 — Cloudflare Workers (`worker/`)

| Worker             | File                       | Config                                | Route                          | Deploy            |
|--------------------|----------------------------|---------------------------------------|--------------------------------|-------------------|
| `ecdotica-adsense` | `ecdotica-adsense.js`      | `wrangler.ecdotica-adsense.toml`      | `ecdotica.com/*`               | CI on push to main |
| `ecdotica-analyzer`| (linked directly to repo)  | —                                     | `ecdotica.com/analyzer*`       | CI on push to main |
| `ecdoticon`        | `ecdoticon.js`             | `wrangler.ecdoticon.toml`             | `ecdotica.com/api/ecdoticon`   | Manual            |
| `ecdotica-api`     | `index.js`                 | `wrangler.toml`                       | `*.workers.dev` only           | Manual            |

Manual deploy:

```bash
npx wrangler deploy --config wrangler.ecdoticon.toml
npx wrangler deploy --config wrangler.toml
```

Secrets are set via `wrangler secret put <NAME>`, never committed.

**Important context:**
- `api.ecdotica.com` is a CNAME to Railway (`sweet-luck-production.up.railway.app`), **not** a Worker.
- `ecdotica-adsense` serves `/ads.txt` (Google AdSense pub-7917471830627014) and passes everything else through to the WordPress origin.
- `ecdotica-plagiarism-checker` was deleted on 2026-03-05 (exposed API keys, no active routes).

### `worker/index.js` — `ecdotica-api`

Two POST endpoints:
- `/api/v1/manuscripts/upload` — multipart form upload (rejects `.pdf` with a 415 + `fallback_endpoint` to Railway).
- `/api/v1/manuscripts/submit` — JSON body `{ text }` or `{ content }`.

`analyzeManuscript(text, env)` computes a comprehensive analysis in pure JS: word/sentence/paragraph stats, vocabulary diversity (TTR), adjective/adverb ratios, dialog detection, Flesch reading level, connective coherence, verb-tense distribution, proper-noun extraction, a 0-100 `quality_score`, and an `editorial_status` verdict (`ACCEPTED`, `ACCEPTED_WITH_REVISIONS`, `REVIEW_NEEDED`, `MAJOR_REVISION`, `REJECTED`).

Plagiarism detection lives in `detectPlagiarism(text, env)` — extracts up to 18 key phrases, queries Google Custom Search (`GOOGLE_API_KEY` + `GOOGLE_SEARCH_ENGINE_ID`), and scores semantic similarity via 3-gram Jaccard/cosine. Output includes `originalidad`, `plagio`, `estado` (`Aprobado` / `Revisión menor` / `Sospechoso` / `Plagio detectado`), and ranked `coincidencias`.

The bundle is the wrangler-produced output (functions wrapped with `__name(...)`, source map reference at bottom). When editing, keep the bundled structure intact and re-deploy; don't try to "clean up" the IIFE-style declarations.

### `worker/ecdoticon.js` — Literary Chatbot

Editorial assistant for `ecdotica.com`. Spanish-language, Bolivian-literature focused.

**Endpoints:**
- `GET /health`, `GET /diag/openai`
- `GET /api/ecdoticon/widget.css?theme=auto|light|dark` — responsive widget CSS
- `GET|POST /api/ecdoticon/chat` (also `/chat`) — params `q`, `mode` (`strict`/`hybrid`/`open`), `depth` (`breve`/`medio`/`profundo`), `student` (bool), `history` (array)

**Key pieces:**
- `CANON` array — hand-curated knowledge base of Bolivian authors, works, and publishers (Jaime Saenz, Adela Zamudio, Liliana Colanzi, Hermanos Loayza, etc.) with aliases, bios, editorial guidance, and a `wiki.allow` flag.
- `findCanon(query)` — alias matching with longest-match preference. `disambiguatePazSoldan` resolves the Marcelo/Edmundo ambiguity.
- `GUARDS` — per-author sanitizers (banned regex sentences + replacements) applied to the model output to correct common factual errors (e.g. Jaimes Freyre's birthplace, Nataniel Aguirre's birth year, classifying Colanzi as a short-story author not a novelist).
- `searchEcdotica(query)` — hits `https://ecdotica.com/wp-json/ecdoticon/v1/search` for site results.
- `searchWikipedia(query)` — fetched only when `ALLOW_WIKIPEDIA=true` *and* the query/canon hit appears in `DEFAULT_WIKI_WHITELIST` or `WIKI_WHITELIST` env.
- `callOpenAIWithTimeout(env, messages, timeoutMs, opts)` — uses `OPENAI_MODEL` (default `gpt-4o-mini`), 25s timeout, structured JSON logging via `log(level, event, data, requestId)`.

When editing `CANON` or `GUARDS`:
- Keep aliases lowercased, accent-stripped variants included (both `hasbún` and `hasbun`, both `wiethüchter` and `wiethuchter`).
- New `strict: true` entries restrict the model to context only.
- Date/biography corrections should land as `GUARDS[id].replace` regexes, not in the canon bio, so they survive context drift.

### `worker/ecdotica-adsense.js`

Two-screen Worker. Serves `/ads.txt` inline; passes everything else to the WordPress origin via `fetch(request)`. Update the AdSense publisher ID here if it changes.

---

## Component 3 — WordPress Plugin (`wordpress-plugin/`)

**`ecdotica-ai-assistant.php`** — "Ecdótica Analyzer v2" (v2.0.0). Installed in production at `wp-content/plugins/ecdotica-ai-assistant/` on `ecdotica.com`.

- Defines `ECDOTICA_API_BASE_URL = 'https://api.ecdotica.com/api/v1'` and `ECDOTICA_API_TIMEOUT = 300` (5 minutes for RAG analysis).
- `ecdotica_analyze_manuscript_rag($file_path, $author, $title)` — POSTs the file (PDF) to `/manuscripts/analyze-rag` via cURL.
- `ecdotica_analyzer_shortcode()` — `[ecdotica_analyzer]` shortcode renders the upload form + result panel (vanilla jQuery + inline CSS).

Endpoints the plugin consumes (all on Railway, **not** in this repo):
- `POST /api/v1/text/analyze`
- `POST /api/v1/manuscripts/check-plagiarism`
- `POST /api/v1/analyze`
- `POST /api/v1/manuscripts/analyze-rag`
- `GET  /api/v1/reports/{id}`

`wordpress-plugin/README.md` notes that the other plugin files (`admin-page.php`, `config.php`, `database-setup.php`) are not yet extracted from wp-admin. When extracting them, paste-and-commit the raw production file, preserving any oddities (mixed tab/space indentation in `ecdotica-ai-assistant.php` is faithful to the production copy — don't reformat).

---

## Code Conventions

### Naming

| Kind         | Convention                  | Example                                |
|--------------|-----------------------------|----------------------------------------|
| Functions    | `snake_case` (Spanish)      | `contar_palabras`, `evaluar_novela`    |
| Classes      | `PascalCase`                | `EditorDeTexto`, `ProcesadorDeArchivos`|
| Constants    | `UPPER_SNAKE_CASE`          | `GENERO_CRITERIOS`, `CANON`            |
| Files        | `snake_case.py` / `kebab-case.js` | `evaluador.py`, `ecdotica-adsense.js` |

### Language

All identifiers, docstrings, comments, user-facing output, and commit messages are in **Spanish**. JavaScript identifiers in `worker/` are English for technical reasons (the bundles are minified output), but log events, user-visible strings, and CANON content stay Spanish.

### Docstrings

Spanish, one short line describing intent. Add inline usage notes only when the call site needs them.

```python
def contar_palabras(texto):
    """Cuenta el número total de palabras en el texto."""
    return len(re.findall(r'\w+', texto))
```

### Error Handling

- Optional NLP dependencies (`PyPDF2`, `docx`, `spacy`, `language_tool_python`) are wrapped in `try/except ImportError` and degrade silently — preserve this pattern.
- Use `ValueError` for unsupported genre names (`evaluar_manuscrito`).
- Use standard `FileNotFoundError` semantics for missing manuscript files (let `open()` raise).

### Indentation

All Python code uses 4-space indentation. Older notes about "broken indentation" no longer apply — the tree was normalized. Do not introduce tabs.

---

## Design Patterns

| Pattern               | Where Used                                                       |
|-----------------------|------------------------------------------------------------------|
| **Dispatch table**    | `GENERO_CRITERIOS` in `evaluador.py`; `CANON` lookup in `ecdoticon.js` |
| **Strategy**          | Each `criterios/<genre>.py` is a swappable evaluation strategy   |
| **Template method**   | All `evaluar_<genero>(stats)` share one signature + result shape |
| **Graceful degradation** | Optional imports → degraded mode; missing CSE keys → "Sin verificar" |
| **Sanitization layer**| `GUARDS` in `ecdoticon.js` applies regex fixes to LLM output     |

---

## Development Workflow

### Branch Naming (from CONTRIBUTING.md)

```
feature/descripcion-breve
fix/descripcion-breve
```

### Commit Message Format

Two coexisting styles in the history; either is acceptable:

```
[TIPO] Descripción clara del cambio        # CONTRIBUTING.md style
tipo(scope): descripción breve              # Conventional Commits style
```

Types: `feat` / `[FEAT]`, `fix` / `[FIX]`, `docs` / `[DOCS]`, `style` / `[STYLE]`, `test` / `[TEST]`, `chore`, `infra` / `[INFRA]`.

### Pull Request Requirements

- Code follows project style guide (Spanish identifiers, 4-space Python indentation)
- Tests included for new analyzer functionality
- Documentation updated (README and/or CLAUDE.md when behavior or structure changes)
- No conflicts with `main`
- At least one approved review
- Related Issues referenced (`Closes #N`)

---

## Adding a New Genre

To add a genre (e.g., a new `microrelato`):

1. Create `src/procesamiento/criterios/microrelato.py` with `evaluar_microrelato(stats)` returning the standard four-criterion result dict (`ortografia_gramatica`, `longitud`, `estructura`, `legibilidad`).
2. Register it in `src/procesamiento/criterios/__init__.py`:
   ```python
   from . import novela, cuento, poema, ensayo, cronica, microrelato
   __all__ = [..., 'microrelato']
   ```
3. Register it in `src/procesamiento/evaluador.py`:
   ```python
   from criterios import novela, cuento, poema, ensayo, cronica, microrelato
   GENERO_CRITERIOS['microrelato'] = microrelato.evaluar_microrelato
   ```
4. Add `'microrelato'` to `GENEROS_DISPONIBLES` in `main.py`.
5. Add tests to `tests/test_criterios.py` (new `TestMicrorelato` class + a `stats_microrelato_apto` fixture).
6. Add a row to the genre criteria table in this file.
7. Optionally create `src/microrelato/reglas.py` if genre-specific business logic (beyond evaluation criteria) is needed.

---

## Services & External Dependencies

| Service          | Purpose                                | Secret(s)                                   |
|------------------|----------------------------------------|---------------------------------------------|
| Railway          | FastAPI backend (`api.ecdotica.com`)   | `DATABASE_URL`, `OPENAI_API_KEY`, `BRAVE_API_KEY` |
| Cloudflare       | CDN, DNS, Workers                      | Per-Worker via `wrangler secret put`        |
| OpenAI           | `ecdoticon` chatbot + Railway analysis | `OPENAI_API_KEY`, `OPENAI_MODEL`            |
| Google CSE       | Plagiarism detection in `ecdotica-api` | `GOOGLE_API_KEY`, `GOOGLE_SEARCH_ENGINE_ID` |
| Brave Search     | Plagiarism detection on Railway        | `BRAVE_API_KEY`                             |
| Stripe / PayPal  | WooCommerce subscriptions              | Configured in WooCommerce admin             |
| Google AdSense   | Monetization (pub-7917471830627014)    | Served via `ecdotica-adsense` Worker        |
| EasyWP           | WordPress hosting (origin)             | —                                           |

---

## What Does Not Live in This Repo

- The **Railway FastAPI backend** (`api.ecdotica.com`) is a separate codebase — endpoints like `/api/v1/manuscripts/analyze-rag` and `/api/v1/manuscripts/check-plagiarism` are not implemented here.
- The **`ecdotica-analyzer` Worker** is linked directly to the repo from Cloudflare; there is no source file in `worker/`. Don't try to "find" it locally.
- The **WordPress site theme and most plugins** live in WP-admin only. The `wordpress-plugin/` directory holds extracted source for Ecdótica's own plugin.

## What Does Not Exist Yet

- `setup.py` / `pyproject.toml` (no formal Python package definition)
- CI/CD inside this repo (no `.github/workflows/`); CI for Workers is configured on Cloudflare's side.
- Docker / deployment configuration for the Python analyzer
- A unified HTTP/CLI gateway that proxies between the Python analyzer and the JS Workers

---

## Sample Data

`src/samples/sample.txt` contains *"Amor sin libertad"* by Yuri Ortuño León, used by `archivos.analizar_texto_ejemplo()` and `archivos.obtener_estadisticas_texto()` as the reference input. Do not delete or modify it.
