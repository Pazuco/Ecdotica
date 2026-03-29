# Implementation Plan: Soporte PDF y DOCX

**Branch**: `002-soporte-pdf-docx` | **Date**: 2026-03-29 | **Spec**: [spec.md](spec.md)

## Summary

Conectar `ProcesadorDeArchivos` (ya implementado en `archivos.py`) al pipeline principal
para que `analizar_manuscrito` en `utils.py` y el punto de entrada `main.py` acepten
archivos `.pdf` y `.docx` además de `.txt`. No se modifica la lógica de evaluación por género.

## Technical Context

**Language/Version**: Python 3.x
**Primary Dependencies**: PyPDF2 ≥ 3.0.0, python-docx ≥ 0.8.11 (ambas opcionales, ya en requirements.txt)
**Storage**: N/A — archivos locales en sistema de ficheros
**Testing**: pytest ≥ 7.0.0
**Target Platform**: Linux/macOS/Windows (CLI local)
**Project Type**: CLI tool / biblioteca
**Performance Goals**: Extracción de texto en tiempo razonable para manuscritos de hasta 150,000 palabras
**Constraints**: Degradación elegante si PyPDF2 o python-docx no están instalados
**Scale/Scope**: Un archivo a la vez, uso editorial local

## Constitution Check

| Principio | Estado | Notas |
|---|---|---|
| I. Español como lengua | ✅ | Todos los mensajes de error en español |
| II. Una función evaluadora por género | ✅ | No se toca la lógica de criterios |
| III. TDD obligatorio | ✅ | Tests se escriben antes de implementar |
| IV. Degradación elegante | ✅ | ImportError manejado para PyPDF2 y python-docx |
| V. Simplicidad — YAGNI | ✅ | Solo se añade detección de extensión y enrutamiento; sin OCR, sin nuevas abstracciones |

**Veredicto**: Sin violaciones. Proceder.

## Project Structure

### Documentation (this feature)

```text
specs/002-soporte-pdf-docx/
├── plan.md              ← este archivo
├── research.md          ← Phase 0
├── contracts/           ← Phase 1
│   └── cli-contract.md
└── checklists/
    └── requirements.md  ← ya creado
```

### Source Code (archivos modificados)

```text
src/procesamiento/
├── utils.py             ← modificar analizar_manuscrito() para multi-formato
└── archivos.py          ← ProcesadorDeArchivos ya existe, sin cambios necesarios

main.py                  ← sin cambios (ya llama a analizar_manuscrito)

tests/
└── test_utils.py        ← agregar tests para PDF y DOCX
```

**Structure Decision**: Proyecto único CLI. Se reutiliza `ProcesadorDeArchivos` existente.
La única modificación de lógica va en `analizar_manuscrito` — detecta la extensión y delega
la extracción al procesador antes de pasar el texto al pipeline existente.

## Phase 0: Research

### Decisiones técnicas

**Decisión**: Reutilizar `ProcesadorDeArchivos` de `archivos.py` en lugar de reimplementar
la extracción en `utils.py`.
- **Rationale**: La clase ya existe, maneja los tres formatos y tiene degradación elegante.
  Duplicar la lógica violaría el principio V (Simplicidad).
- **Alternativa rechazada**: Agregar extracción inline en `analizar_manuscrito` — más simple
  inicialmente pero duplica código ya probado.

**Decisión**: Detectar formato por extensión de archivo (no por magic bytes).
- **Rationale**: Consistente con el comportamiento actual de `ProcesadorDeArchivos`. Suficiente
  para el caso de uso editorial donde los archivos tienen extensiones correctas.
- **Alternativa rechazada**: Detectar por magic bytes — más robusto pero complejidad innecesaria
  (principio V).

**Decisión**: Mensajes de error en español con el comando `pip install` exacto.
- **Rationale**: Los editores no son necesariamente técnicos; el mensaje debe ser accionable.

## Phase 1: Design & Contracts

### Contrato CLI actualizado

`analizar_manuscrito(path)` — nueva firma conceptual:

```
Entrada:  ruta a archivo .txt, .pdf o .docx
Salida:   dict { num_palabras, num_capitulos, indice_legibilidad, errores_graves }
Errores:
  - FileNotFoundError si el archivo no existe
  - ValueError si el formato no está soportado (con lista de formatos válidos)
  - Mensaje informativo (no excepción) si falta dependencia opcional
```

`main.py` — sin cambios de interfaz. Acepta los mismos argumentos `<ruta> <genero>`.

### Archivos a modificar

| Archivo | Cambio |
|---|---|
| `src/procesamiento/utils.py` | `analizar_manuscrito`: detectar extensión, usar `ProcesadorDeArchivos` para pdf/docx, mantener lectura directa para txt |
| `tests/test_utils.py` | Agregar `TestAnalizarManuscritoPDF` y `TestAnalizarManuscritoDocx` con archivos de prueba mínimos |

### Archivos sin cambios

- `src/procesamiento/archivos.py` — `ProcesadorDeArchivos` se usa tal cual
- `main.py` — ya llama a `analizar_manuscrito`, funcionará automáticamente
- Todos los módulos de criterios — no se tocan
- `evaluador.py` — no se toca
