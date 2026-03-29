# Tasks: Soporte PDF y DOCX

**Input**: `specs/002-soporte-pdf-docx/plan.md` y `spec.md`
**Branch**: `002-soporte-pdf-docx`

---

## Phase 1: Fundacional

**Purpose**: Tests en rojo antes de tocar código de producción (TDD obligatorio — Principio III)

- [ ] T001 [US1] Escribir `TestAnalizarManuscritoDocx` en `tests/test_utils.py` con fixture de archivo `.docx` mínimo — verificar que falla antes de implementar
- [ ] T002 [US2] Escribir `TestAnalizarManuscritoPdf` en `tests/test_utils.py` con fixture de archivo `.pdf` mínimo — verificar que falla antes de implementar
- [ ] T003 [P] [US3] Escribir test de formato no soportado en `tests/test_utils.py` — verificar que falla antes de implementar

**Checkpoint**: `pytest tests/test_utils.py` muestra los nuevos tests en ROJO. Los 48 tests existentes siguen en verde.

---

## Phase 2: User Story 1 — Soporte DOCX (Priority: P1) 🎯 MVP

**Goal**: `analizar_manuscrito` acepta archivos `.docx` y produce el mismo dict de stats que con `.txt`.

**Independent Test**: `python main.py manuscrito.docx novela` produce un reporte `APTO`/`NO APTO`.

### Implementación

- [ ] T004 [US1] Modificar `analizar_manuscrito(path)` en `src/procesamiento/utils.py`:
  - Detectar extensión del archivo
  - Para `.docx`: usar `ProcesadorDeArchivos().extraer_texto(path)` de `archivos.py`
  - Para `.txt`: mantener comportamiento actual
  - Para extensiones no soportadas: lanzar `ValueError` con lista de formatos válidos
- [ ] T005 [US1] Manejar el caso en que python-docx no está instalado: capturar el mensaje de error de `ProcesadorDeArchivos` y relanzarlo como `ImportError` con instrucción `pip install python-docx`

**Checkpoint**: `pytest tests/test_utils.py::TestAnalizarManuscritoDocx` en VERDE. Tests existentes siguen en verde.

---

## Phase 3: User Story 2 — Soporte PDF (Priority: P2)

**Goal**: `analizar_manuscrito` acepta archivos `.pdf` con texto seleccionable.

**Independent Test**: `python main.py manuscrito.pdf ensayo` produce un reporte coherente.

### Implementación

- [ ] T006 [US2] Extender la detección de extensión en `analizar_manuscrito` para `.pdf`:
  - Usar `ProcesadorDeArchivos().extraer_texto(path)` para `.pdf`
  - Detectar si el texto extraído es vacío o es el mensaje de error de PyPDF2 ausente
  - Informar al usuario con mensaje claro y comando `pip install PyPDF2`
- [ ] T007 [US2] Manejar PDF sin texto extraíble (escaneado): si el texto está vacío tras extracción, lanzar `ValueError` con mensaje descriptivo

**Checkpoint**: `pytest tests/test_utils.py::TestAnalizarManuscritoPdf` en VERDE. Todos los tests en verde.

---

## Phase 4: User Story 3 — Formato no soportado (Priority: P3)

**Goal**: Archivos con extensión desconocida producen error claro, no excepción técnica.

**Independent Test**: `python main.py manuscrito.odt novela` muestra mensaje con formatos válidos.

### Implementación

- [ ] T008 [US3] Verificar que el `ValueError` de formato no soportado (ya cubierto en T004) incluye la lista `['.txt', '.pdf', '.docx']` en el mensaje

**Checkpoint**: `pytest tests/test_utils.py` — todos los tests en verde incluyendo los nuevos.

---

## Phase 5: Cierre

- [ ] T009 [P] Actualizar `CLAUDE.md`: reflejar que `analizar_manuscrito` ahora acepta multi-formato
- [ ] T010 Ejecutar suite completa: `pytest tests/ -v` — los 48+ tests en verde
- [ ] T011 Commit con mensaje `[FEAT] Soporte de manuscritos en PDF y DOCX`

---

## Dependencias y orden de ejecución

- **Phase 1** (tests RED): sin dependencias, empieza aquí
- **Phase 2** (DOCX): depende de Phase 1 — T004 y T005 secuenciales entre sí
- **Phase 3** (PDF): puede empezar en paralelo con Phase 2 una vez T004 esté completo
- **Phase 4** (formato inválido): depende de T004
- **Phase 5** (cierre): depende de Phases 2, 3 y 4

### Notas

- `[P]` = puede correr en paralelo (archivos distintos, sin dependencias)
- Verificar RED antes de implementar en cada fase (TDD)
- No modificar `archivos.py` — `ProcesadorDeArchivos` se usa tal cual
- No modificar `main.py` — funciona automáticamente al cambiar `analizar_manuscrito`
