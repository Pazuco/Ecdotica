<!--
Sync Impact Report
Version change: N/A → 1.0.0 (initial ratification)
Added sections: Core Principles, Convenciones de código, Flujo de desarrollo, Governance
Removed sections: none (new document)
Templates requiring updates: none pending
Follow-up TODOs: none
-->

# Ecdotica Constitution

## Core Principles

### I. Español como lengua del proyecto
Todo identificador, docstring, comentario y salida visible al usuario DEBE estar en español.
Las únicas excepciones permitidas son nombres de librerías externas, convenciones técnicas
estándar (pytest, PEP 8) y palabras sin traducción establecida en el dominio técnico.

### II. Una función evaluadora por género (NON-NEGOTIABLE)
Cada género literario DEBE tener exactamente una función `evaluar_<genero>(stats)` en
`src/procesamiento/criterios/<genero>.py`. La firma y el esquema de retorno son
invariables: `{'cumple': bool, 'mensaje': str}` por criterio. No se permiten
evaluadores monolíticos ni lógica de género mezclada entre módulos.

### III. TDD obligatorio
Toda función nueva DEBE tener tests antes de su implementación (Red → Green → Refactor).
Los tests viven en `tests/` y se ejecutan con `pytest tests/ -v`. El CI en GitHub Actions
es la puerta de calidad: ningún código llega a `main` sin pasar los 48+ tests existentes.

### IV. Degradación elegante de dependencias opcionales
SpaCy, LanguageTool, PyPDF2 y python-docx son opcionales. Su ausencia NO debe
interrumpir el flujo principal. Todo import de estas bibliotecas DEBE estar envuelto
en `try/except ImportError` con un mensaje claro de degradación.

### V. Simplicidad — YAGNI
No se implementa lo que no está en los criterios editoriales definidos. Sin flags de
compatibilidad hacia atrás, sin abstracciones especulativas. Tres líneas similares son
preferibles a una abstracción prematura.

## Convenciones de código

- **Indentación**: 4 espacios (PEP 8). Sin tabs.
- **Funciones**: `snake_case` con palabras en español (`contar_palabras`, `evaluar_novela`).
- **Clases**: `PascalCase` (`EditorDeTexto`, `ProcesadorDeArchivos`).
- **Constantes**: `UPPER_SNAKE_CASE` (`GENERO_CRITERIOS`).
- **Archivos**: `snake_case.py`.
- Commits con prefijo: `[FEAT]`, `[FIX]`, `[DOCS]`, `[STYLE]`, `[TEST]`.

## Flujo de desarrollo

1. Crear rama `feature/descripcion-breve` o `fix/descripcion-breve`.
2. Escribir tests (RED).
3. Implementar hasta pasar tests (GREEN).
4. Refactorizar si aplica (REFACTOR).
5. Verificar que los 48+ tests existentes siguen en verde.
6. PR contra `main` con al menos una revisión aprobada.

## Governance

Esta constitución DEBE ser la fuente de verdad para todas las decisiones de diseño.
Enmiendas requieren: (a) justificación documentada, (b) actualización de `CLAUDE.md`,
(c) versionado semántico en este documento.

El archivo `CLAUDE.md` es la guía operativa para el agente AI; esta constitución
son los principios no negociables que lo gobiernan.

**Version**: 1.0.0 | **Ratified**: 2026-03-29 | **Last Amended**: 2026-03-29
