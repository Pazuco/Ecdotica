# Feature Specification: Detección real de errores ortográficos y gramaticales

**Feature Branch**: `001-integrar-languagetool`
**Created**: 2026-03-29
**Status**: Draft
**Input**: Integrar LanguageTool en detectar_errores para reemplazar el valor hardcodeado con detección real de errores ortográficos y gramaticales en el texto

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evaluación honesta de calidad lingüística (Priority: P1)

Un editor de Editorial Nuevo Milenio somete un manuscrito a evaluación. Actualmente el
sistema siempre reporta 5 errores sin importar el contenido real del texto. El editor
necesita que el número de errores refleje los errores reales del manuscrito para tomar
decisiones de aceptación o rechazo informadas.

**Why this priority**: Sin detección real, el criterio de ortografía/gramática es inútil.
Es el stub más crítico del sistema.

**Independent Test**: Se puede verificar enviando dos textos — uno impecable y uno lleno
de errores — y confirmando que los conteos son distintos y proporcionales a los errores reales.

**Acceptance Scenarios**:

1. **Given** un texto en español sin errores ortográficos ni gramaticales,
   **When** se analiza el manuscrito,
   **Then** el número de errores reportado es 0 o cercano a 0.

2. **Given** un texto con errores ortográficos evidentes (palabras mal escritas),
   **When** se analiza el manuscrito,
   **Then** el número de errores reportado es mayor que el de un texto sin errores.

3. **Given** LanguageTool no está instalado en el sistema,
   **When** se analiza el manuscrito,
   **Then** el sistema no lanza excepción sino que informa la degradación y usa un valor predeterminado.

---

### User Story 2 - Resultados consistentes con los umbrales por género (Priority: P2)

Los criterios editoriales definen umbrales de errores distintos por género (ej. novela:
< 10 por 10,000 palabras; poema: < 5 por 1,000 palabras). El editor necesita que los
errores detectados sean comparables entre manuscritos para que los umbrales tengan sentido.

**Why this priority**: Si la detección es real pero inconsistente, los umbrales pierden validez.

**Independent Test**: Dos manuscritos del mismo género con diferente calidad lingüística
deben producir conteos proporcionales que permitan distinguir cuál supera el umbral.

**Acceptance Scenarios**:

1. **Given** un cuento de 5,000 palabras con 8 errores reales,
   **When** se evalúa con el criterio de cuento (< 5 errores por 5,000 palabras),
   **Then** el criterio `ortografia_gramatica` retorna `cumple: False`.

2. **Given** un cuento de 5,000 palabras con 2 errores reales,
   **When** se evalúa con el criterio de cuento,
   **Then** el criterio `ortografia_gramatica` retorna `cumple: True`.

---

### Edge Cases

- ¿Qué ocurre si el texto está vacío o tiene menos de 10 palabras?
- ¿Qué ocurre si LanguageTool tarda demasiado en textos muy largos?
- ¿Qué ocurre si el texto contiene mezcla de idiomas (ej. citas en latín)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE detectar errores ortográficos y gramaticales reales en textos en español.
- **FR-002**: La función `detectar_errores(texto)` DEBE retornar un entero que represente el número de errores encontrados.
- **FR-003**: El sistema DEBE manejar la ausencia de LanguageTool sin interrumpir el flujo de evaluación.
- **FR-004**: Los errores detectados DEBEN ser consistentes: el mismo texto analizado dos veces DEBE producir el mismo conteo.
- **FR-005**: Si LanguageTool no está disponible, el sistema DEBE notificarlo y retornar un valor que no bloquee la evaluación.

### Key Entities

- **Error lingüístico**: Ocurrencia de un problema ortográfico o gramatical detectado en el texto del manuscrito.
- **Texto de manuscrito**: Cadena de caracteres en español que representa el contenido a evaluar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un texto sin errores ortográficos ni gramaticales recibe un conteo de 0 errores.
- **SC-002**: Un texto con errores introducidos intencionalmente recibe un conteo mayor que el mismo texto corregido.
- **SC-003**: La función no lanza excepciones en ningún escenario (texto vacío, LanguageTool ausente, texto muy largo).
- **SC-004**: Los 48 tests existentes del proyecto continúan pasando sin modificación.

## Assumptions

- LanguageTool se usa con el idioma `es` (español general), no variantes regionales específicas.
- El conteo de errores se refiere a errores *graves* (ortografía y gramática), no sugerencias de estilo.
- El rendimiento es aceptable para textos de hasta 150,000 palabras (máximo de una novela según criterios del proyecto).
- La integración con LanguageTool ya existe como referencia en `archivos.py` y puede ser adaptada.
