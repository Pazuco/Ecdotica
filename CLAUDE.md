# CLAUDE.md — Ecdotica

AI assistant reference for the Ecdotica codebase. Keep this file up to date as the project evolves.

---

## Project Overview

**Ecdotica** is a Spanish-language literary analysis platform for automated manuscript evaluation, developed for **Editorial Nuevo Milenio** (a publishing house). It applies digital ecdotics — the science of text transmission and critical editing — to automate the review of manuscript submissions by literary genre.

- **Language:** Python 3.x
- **License:** MIT (Copyright 2025 Pazuco)
- **Domain:** Natural language processing, literary analysis, editorial automation
- **Primary language of codebase:** Spanish (variable/function names, docstrings, comments, output)

---

## Repository Structure

```
Ecdotica/
├── main.py                        # Entry point placeholder (minimal)
├── README.md                      # High-level project overview (Spanish)
├── CONTRIBUTING.md                # Detailed contribution guide (Spanish)
├── LICENSE                        # MIT License
├── .gitignore                     # Standard Python gitignore
└── src/
    ├── editor.py                  # Text editing utilities (EditorDeTexto class)
    ├── samples/
    │   └── sample.txt             # Sample: "Amor sin libertad" by Yuri Ortuño
    ├── novela/                    # Novel module (placeholder)
    │   ├── __init__.py
    │   └── reglas.py
    ├── cuento/                    # Short story module (placeholder)
    │   ├── __init__.py
    │   └── reglas.py
    ├── poema/                     # Poetry module (placeholder)
    │   ├── __init__.py
    │   └── reglas.py
    ├── ensayo/                    # Essay module (placeholder)
    │   ├── __init__.py
    │   └── reglas.py
    ├── cronica/                   # Chronicle module (placeholder)
    │   ├── __init__.py
    │   └── reglas.py
    └── procesamiento/             # Core processing pipeline
        ├── README.md              # Processing module documentation
        ├── evaluador.py           # Central evaluation orchestrator
        ├── archivos.py            # File handling (PDF, DOCX, TXT) + SpaCy/LanguageTool
        ├── utils.py               # Text analysis utilities
        └── criterios/             # Genre-specific evaluation criteria
            ├── __init__.py
            ├── novela.py          # Novel criteria (30k–150k words, 3+ chapters, legibility ≥50)
            └── cuento.py          # Short story criteria (1k–30k words, legibility ≥60)
```

---

## Core Modules

### `src/procesamiento/evaluador.py` — Evaluation Pipeline

Central orchestrator. Maps genres to their evaluation functions and generates text reports.

```python
GENERO_CRITERIOS = {
    'novela': novela.evaluar_novela,
    'cuento': cuento.evaluar_cuento,
}
```

**Key functions:**
- `evaluar_manuscrito(stats, genero)` — Dispatches to genre-specific evaluator; raises `ValueError` for unimplemented genres.
- `reporte_resultados(resultados, genero)` — Formats results as a checklist report with `✓`/`✗` and `APTO`/`NO APTO` verdict.

**CLI usage:**
```bash
python src/procesamiento/evaluador.py <ruta_manuscrito> <genero>
```

---

### `src/procesamiento/utils.py` — Text Analysis Utilities

Regex-based text statistics. No external dependencies.

| Function | Description |
|---|---|
| `contar_palabras(texto)` | Word count via `\w+` regex |
| `contar_capitulos(texto)` | Detects `Capítulo` at start of line (case-insensitive, handles accented í) |
| `calcular_legibilidad(texto)` | Flesch-Kincaid adaptation for Spanish |
| `detectar_errores(texto)` | **Stub** — currently hardcoded to return `5`. Replace with LanguageTool integration. |
| `analizar_manuscrito(path)` | Reads a `.txt` file and returns a `stats` dict |

**Stats dict schema:**
```python
{
    'num_palabras': int,
    'num_capitulos': int,
    'indice_legibilidad': float,  # 0–100
    'errores_graves': int
}
```

---

### `src/procesamiento/archivos.py` — File Processing

Handles multi-format manuscript ingestion and NLP integration.

**`ProcesadorDeArchivos` class:**
- `extraer_texto(ruta)` — Dispatches by extension (`.pdf`, `.docx`, `.txt`)
- `_extraer_pdf(ruta)` — Uses `PyPDF2` (gracefully degrades if not installed)
- `_extraer_docx(ruta)` — Uses `python-docx` (gracefully degrades if not installed)
- `_extraer_txt(ruta)` — Standard UTF-8 read

**Standalone NLP functions (require SpaCy + LanguageTool):**
- `analizar_texto_ejemplo()` — Demonstrates full NLP pipeline on `samples/sample.txt`: entity recognition, token analysis, sentence segmentation, LanguageTool spell check.
- `obtener_estadisticas_texto(ruta_archivo)` — Returns SpaCy-powered stats dict: characters, words, sentences, tokens, named entities.

---

### `src/procesamiento/criterios/` — Genre Evaluation Criteria

Each genre module exports a single `evaluar_<genero>(stats)` function returning a results dict.

**Results dict schema (per criterion):**
```python
{
    'cumple': bool,
    'mensaje': str,
    # + genre-specific extra fields
}
```

**Genre criteria table:**

| Genre | Word Range | Chapters | Error Threshold | Legibility Min |
|---|---|---|---|---|
| `novela` | 30,000–150,000 | ≥ 3 required | < 10 per 10,000 words | ≥ 50 |
| `cuento` | 1,000–30,000 | Not required | < 5 per 5,000 words | ≥ 60 |
| `poema` | Not implemented | — | — | — |
| `ensayo` | Not implemented | — | — | — |
| `cronica` | Not implemented | — | — | — |

---

### `src/editor.py` — Text Editor Utilities

`EditorDeTexto` class for basic text correction detection:
- `encontrar_espacios_dobles()` — Detects double spaces
- `falta_puntuacion()` — Checks for missing punctuation
- `errores_comunes()` — Common typo patterns

---

## Dependencies

No `requirements.txt` exists yet. Install manually:

```bash
# Core NLP
pip install spacy
python -m spacy download es_core_news_sm

# Grammar checking
pip install language-tool-python

# Document parsing
pip install PyPDF2
pip install python-docx
```

**SpaCy models available:**
- `es_core_news_sm` — Small (default, fast)
- `es_core_news_md` — Medium
- `es_core_news_lg` — Large (most accurate)

**LanguageTool language codes:**
- `'es'` or `'es-ES'` for Spanish

Both `PyPDF2` and `python-docx` are optional — `archivos.py` degrades gracefully with an error message string if they are absent.

---

## Code Conventions

### Naming

| Kind | Convention | Example |
|---|---|---|
| Functions | `snake_case` (Spanish words) | `contar_palabras`, `evaluar_novela` |
| Classes | `PascalCase` | `EditorDeTexto`, `ProcesadorDeArchivos` |
| Constants | `UPPER_SNAKE_CASE` | `GENERO_CRITERIOS` |
| Files | `snake_case.py` | `evaluador.py`, `archivos.py` |

### Language

- All identifiers, docstrings, comments, and user-facing output are in **Spanish**.
- Keep this convention for all new code.

### Docstrings

Use Spanish-language docstrings with brief description and, where appropriate, inline usage notes:

```python
def contar_palabras(texto):
    """Cuenta el número total de palabras en el texto."""
    return len(re.findall(r'\w+', texto))
```

### Error Handling

- Use `try/except ImportError` for optional dependencies (`PyPDF2`, `docx`, `spacy`, `language_tool_python`).
- Raise `ValueError` for unsupported genre names.
- Use `FileNotFoundError` semantics for missing manuscript files.

### Known Code Quality Issue — Indentation

Several files (`evaluador.py`, `novela.py`, `cuento.py`) contain **severely inconsistent indentation** — mixed tabs/spaces and misaligned blocks that would cause `IndentationError` at runtime. When modifying these files, normalize all indentation to **4 spaces** per PEP 8. Do not use tabs.

---

## Design Patterns

| Pattern | Where Used |
|---|---|
| **Factory / Dispatch Table** | `GENERO_CRITERIOS` dict in `evaluador.py` maps genre strings to functions |
| **Strategy** | Each `criterios/<genre>.py` encapsulates genre-specific evaluation logic |
| **Template** | All `evaluar_<genero>(stats)` functions share the same signature and return schema |
| **Graceful Degradation** | Optional imports wrapped in `try/except ImportError` |

---

## Development Workflow

### Branch Naming (from CONTRIBUTING.md)

```
feature/descripcion-breve
fix/descripcion-breve
```

### Commit Message Format

```
[TIPO] Descripción clara del cambio
```

Types: `[FEAT]`, `[FIX]`, `[DOCS]`, `[STYLE]`, `[TEST]`

### Pull Request Requirements

- Code follows project style guide
- Tests included for new functionality
- Documentation updated
- No conflicts with `main`
- At least one approved review
- Related Issues referenced (`Closes #N`)

---

## Adding a New Genre

To add a new genre (e.g., `poema`):

1. Create `src/procesamiento/criterios/poema.py` with an `evaluar_poema(stats)` function returning the standard results dict.
2. Register it in `evaluador.py`:
   ```python
   from criterios import novela, cuento, poema

   GENERO_CRITERIOS = {
       'novela': novela.evaluar_novela,
       'cuento': cuento.evaluar_cuento,
       'poema': poema.evaluar_poema,
   }
   ```
3. Implement the `src/poema/reglas.py` module if genre-specific business logic is needed.
4. Add evaluation criteria to the genre table in this file.

---

## Testing

**There is currently no test suite.** No pytest, unittest, or CI/CD configuration exists.

When adding tests:
- Use `pytest`
- Place test files as `test_<module>.py` alongside source modules or in a top-level `tests/` directory
- Follow the pattern: `test_<genero>.py` per genre module (per CONTRIBUTING.md structure)

---

## What Does Not Exist Yet

- `requirements.txt` / `setup.py` / `pyproject.toml`
- Test suite
- CI/CD (no `.github/workflows/`)
- Docker / deployment configuration
- Environment variable / `.env` management
- API / web interface (CLI only)
- Implemented criteria for `poema`, `ensayo`, `cronica`
- Real error detection (currently hardcoded stub in `utils.py:detectar_errores`)

---

## Sample Data

`src/samples/sample.txt` contains *"Amor sin libertad"* by Yuri Ortuño León, used for demonstrating NLP analysis in `archivos.py`. Do not delete or modify it — it is the reference input for `analizar_texto_ejemplo()`.
