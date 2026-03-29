# Feature Specification: Soporte de manuscritos en PDF y DOCX

**Feature Branch**: `002-soporte-pdf-docx`
**Created**: 2026-03-29
**Status**: Draft
**Input**: Conectar ProcesadorDeArchivos al pipeline principal para que main.py y analizar_manuscrito acepten archivos PDF y DOCX además de TXT

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evaluar un manuscrito en DOCX (Priority: P1)

Un autor envía su novela como archivo Word (.docx) — el formato más común en el mundo
editorial. El editor lo evalúa directamente con Ecdotica sin necesidad de convertirlo
manualmente a texto plano.

**Why this priority**: DOCX es el formato estándar de entrega en editorial. Sin soporte,
el editor debe convertir cada manuscrito antes de evaluarlo, lo que hace el sistema
impráctico para uso real.

**Independent Test**: Ejecutar el evaluador con un archivo `.docx` real y verificar que
produce un reporte con veredicto `APTO` o `NO APTO`, igual que con un `.txt`.

**Acceptance Scenarios**:

1. **Given** un manuscrito en formato `.docx`,
   **When** el editor ejecuta la evaluación indicando el género,
   **Then** el sistema extrae el texto y produce un reporte editorial completo.

2. **Given** un archivo `.docx` vacío o sin texto,
   **When** el editor ejecuta la evaluación,
   **Then** el sistema informa que el documento no contiene texto evaluable, sin lanzar excepción.

3. **Given** que python-docx no está instalado,
   **When** el editor intenta evaluar un `.docx`,
   **Then** el sistema informa claramente qué dependencia falta y cómo instalarla.

---

### User Story 2 - Evaluar un manuscrito en PDF (Priority: P2)

Un autor entrega su ensayo en PDF. El editor lo evalúa sin pasos intermedios de conversión.

**Why this priority**: PDF es común para ensayos y crónicas. Es la segunda prioridad
porque la extracción de texto desde PDF es menos fiel que desde DOCX (fuentes embebidas,
columnas, etc.), pero sigue siendo más útil que no soportarlo.

**Independent Test**: Ejecutar el evaluador con un archivo `.pdf` de texto seleccionable
y verificar que produce un reporte coherente con el contenido real.

**Acceptance Scenarios**:

1. **Given** un manuscrito en formato `.pdf` con texto seleccionable,
   **When** el editor ejecuta la evaluación,
   **Then** el sistema extrae el texto y produce un reporte editorial.

2. **Given** un PDF escaneado (solo imagen, sin texto seleccionable),
   **When** el editor ejecuta la evaluación,
   **Then** el sistema informa que no pudo extraer texto del archivo, sin lanzar excepción.

3. **Given** que PyPDF2 no está instalado,
   **When** el editor intenta evaluar un `.pdf`,
   **Then** el sistema informa qué dependencia falta y cómo instalarla.

---

### User Story 3 - Formato no soportado (Priority: P3)

Un editor intenta evaluar un archivo en un formato no reconocido (`.odt`, `.pages`, etc.).

**Why this priority**: Es un caso de error esperado que debe manejarse con un mensaje
claro en lugar de un fallo técnico.

**Independent Test**: Ejecutar el evaluador con un archivo `.odt` y verificar que el
mensaje de error es comprensible y no técnico.

**Acceptance Scenarios**:

1. **Given** un archivo en formato no soportado,
   **When** el editor ejecuta la evaluación,
   **Then** el sistema lista los formatos soportados y termina sin excepción no controlada.

---

### Edge Cases

- ¿Qué ocurre si el archivo PDF está protegido con contraseña?
- ¿Qué ocurre si el DOCX tiene solo imágenes y sin párrafos de texto?
- ¿Qué ocurre si el archivo tiene extensión `.pdf` pero en realidad es otro formato?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE aceptar archivos `.txt`, `.pdf` y `.docx` como entrada para evaluación.
- **FR-002**: El sistema DEBE extraer el texto de cada formato y procesarlo con el mismo pipeline de evaluación existente.
- **FR-003**: Si una dependencia opcional (PyPDF2 o python-docx) no está instalada, el sistema DEBE mostrar un mensaje de error claro con instrucciones de instalación.
- **FR-004**: El sistema DEBE informar al usuario si no puede extraer texto del archivo (PDF escaneado, DOCX vacío).
- **FR-005**: Los formatos no soportados DEBEN producir un mensaje de error comprensible que liste los formatos válidos.
- **FR-006**: El comportamiento para archivos `.txt` NO DEBE cambiar respecto al estado actual.

### Key Entities

- **Manuscrito**: Archivo enviado por el autor en cualquier formato soportado, que contiene el texto a evaluar.
- **Formato de archivo**: Tipo de archivo determinado por su extensión (`.txt`, `.pdf`, `.docx`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un manuscrito en `.docx` produce el mismo reporte editorial que el mismo texto en `.txt`.
- **SC-002**: Un manuscrito en `.pdf` con texto seleccionable produce un reporte editorial coherente.
- **SC-003**: Ningún formato (soportado o no) provoca una excepción no controlada.
- **SC-004**: Los 48 tests existentes continúan pasando sin modificación.
- **SC-005**: Los mensajes de error para dependencias faltantes incluyen el comando de instalación exacto.

## Assumptions

- Se soportan únicamente archivos `.txt`, `.pdf` y `.docx` en esta iteración. `.odt`, `.pages` y otros quedan fuera del alcance.
- La extracción de PDF asume documentos con texto seleccionable; PDFs escaneados no se procesan en esta versión.
- Las dependencias PyPDF2 y python-docx ya están listadas en `requirements.txt` y son opcionales.
- El pipeline de evaluación (criterios, legibilidad, conteo de palabras) no cambia; solo cambia cómo se ingesta el texto inicial.
