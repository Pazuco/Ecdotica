# Guía de Estilo de Comunicación — Ecdotica

Referencia para mantener coherencia en documentación, mensajes de commit, comentarios de código y comunicación del equipo.

---

## Tono

- Directo y técnico. Sin relleno. Si algo puede decirse en diez palabras, no uses veinte.
- Tuteo consistente (`tú`, no `usted`) en toda la documentación dirigida a colaboradores.
- Neutro y colaborativo en revisiones de código: describe el problema, no a la persona.
- El rigor literario que exige el dominio (ecdótica, análisis de manuscritos) no debe traducirse en prosa rebuscada — la claridad es una virtud editorial.

**Frases que suenan bien:**
- "Implementa la función `evaluar_poema` siguiendo el esquema de resultados."
- "Este criterio no cumple el umbral mínimo de legibilidad."
- "Ver `criterios/novela.py` para referencia."

**Frases que suenan mal:**
- "Espero que este mensaje te encuentre bien."
- "Procedemos a efectuar la validación correspondiente."
- "Se ha llevado a cabo la implementación del módulo."

---

## Muestras de Escritura

### Mensaje de commit

```
[FEAT] Agregar evaluador de poema con criterios de legibilidad y longitud

Implementa evaluar_poema(stats) en criterios/poema.py. Registra el género
en GENERO_CRITERIOS. Añade tests en tests/test_criterios.py.
```

### Docstring de función

```python
def calcular_legibilidad(texto):
    """Calcula el índice de legibilidad Flesch-Kincaid adaptado al español.

    Retorna un valor entre 0 y 100. Valores mayores indican mayor facilidad
    de lectura. Usa conteo de sílabas aproximado mediante patrones de vocales.
    """
```

### Comentario en revisión de PR

```
La función `detectar_errores` devuelve 5 hardcodeado — esto bloquea cualquier
evaluación real. Antes de hacer merge habría que conectarlo a LanguageTool o
al menos documentarlo como stub con un TODO explícito.
```

---

## Anti-patrones

- No usar "leverage" ni su traducción forzada "apalancar".
- No abrir mensajes con fórmulas de cortesía vacías.
- No usar voz pasiva donde cabe la activa: "implementa" en vez de "se implementa".
- No mezclar idiomas dentro de un mismo identificador (`get_palabras`, `wordCount`).
- No usar términos en inglés si existe un equivalente español establecido en el proyecto (`palabras`, no `words`; `legibilidad`, no `readability`).
- No escribir docstrings en inglés. Toda la documentación interna es en español.
- No dejar `TODO` sin contexto: incluye qué debe hacerse y por qué.

---

**Última actualización**: Marzo 2026
