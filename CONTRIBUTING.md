# Guía de Contribución a Ecdotica

¡Bienvenido a Ecdotica! Este documento te proporciona las instrucciones necesarias para contribuir al proyecto de análisis de textos literarios con herramientas lingüísticas.

## Tabla de Contenidos

1. [Cómo Usar Issues](#cómo-usar-issues)
2. [Cómo Usar Pull Requests](#cómo-usar-pull-requests)
3. [Áreas de Trabajo por Género Literario](#áreas-de-trabajo-por-género-literario)
4. [Instalación y Uso de SpaCy](#instalación-y-uso-de-spacy)
5. [Instalación y Uso de LanguageTool](#instalación-y-uso-de-languagetool)
6. [Normas de Edición APA](#normas-de-edición-apa)
7. [Configuración de Colaboradores](#configuración-de-colaboradores)

## Cómo Usar Issues

### ¿Qué son los Issues?

Los Issues son espacios para reportar bugs, sugerir mejoras o discutir cambios en el proyecto.

### Crear un Nuevo Issue

1. Ve a la pestaña [Issues](https://github.com/Pazuco/Ecdotica/issues)
2. Haz clic en el botón verde "New issue"
3. Proporciona:
   - **Título claro y descriptivo**
   - **Descripción detallada** del problema o sugerencia
   - **Etiquetas** (labels) relevantes: `bug`, `enhancement`, `documentation`, etc.
   - **Asignación** a colaboradores si es necesario

### Tipos de Issues Recomendados

- **Bug Report**: Describe comportamientos inesperados
- **Feature Request**: Sugiere nuevas funcionalidades
- **Documentation**: Mejoras en la documentación
- **Analysis**: Análisis de nuevos géneros literarios

## Cómo Usar Pull Requests

### ¿Qué es un Pull Request?

Un Pull Request (PR) es una solicitud para integrar cambios en el código principal.

### Flujo de Trabajo

1. **Fork del repositorio**: Crea tu propia copia
   ```bash
   git clone https://github.com/TuUsuario/Ecdotica.git
   cd Ecdotica
   ```

2. **Crea una rama**: Desde la rama `main`
   ```bash
   git checkout -b feature/descripcion-breve
   # o para fixes:
   git checkout -b fix/descripcion-breve
   ```

3. **Realiza los cambios** y haz commits descriptivos
   ```bash
   git add .
   git commit -m "[TIPO] Descripción clara del cambio"
   ```
   Tipos recomendados: `[FEAT]`, `[FIX]`, `[DOCS]`, `[STYLE]`, `[TEST]`

4. **Envía tu rama**
   ```bash
   git push origin feature/descripcion-breve
   ```

5. **Abre un Pull Request** en GitHub con:
   - Descripción clara de qué cambios realiza
   - Referencia a Issues relacionados (ej: "Closes #123")
   - Explicación del por qué de los cambios

6. **Revisor aprueba y realiza el merge**

## Áreas de Trabajo por Género Literario

Ecdotica soporta análisis de diferentes géneros literarios. Organiza tus contribuciones por área:

### Géneros Principales

| Género | Directorio | Descripción |
|--------|-----------|-------------|
| Narrativa | `/narrativa` | Novelas, cuentos, épica |
| Lírica | `/lirica` | Poesía, verso libre |
| Drama | `/drama` | Teatro, diálogos |
| Ensayo | `/ensayo` | Textos argumentativos |
| Crítica | `/critica` | Análisis literarios |

### Estructura de Contribución por Género

```
ecdotica/
├── narrativa/
│   ├── analizador.py
│   ├── modelos.py
│   └── test_narrativa.py
├── lirica/
│   ├── analizador.py
│   ├── metricas.py
│   └── test_lirica.py
└── ...
```

### Colaboración por Especialidad

Si tienes experiencia en un género específico:

1. Crea un Issue señalando tu especialidad
2. Propón análisis, métricas o mejoras para ese género
3. Trabaja en la rama correspondiente
4. Envía PR con documentación específica del género

## Instalación y Uso de SpaCy

SpaCy es una biblioteca de procesamiento de lenguaje natural que Ecdotica utiliza para análisis sintáctico y semántico.

### Instalación

```bash
# Instala SpaCy
pip install spacy

# Descarga el modelo de Spanish
python -m spacy download es_core_news_sm
# Otras opciones: es_core_news_md, es_core_news_lg
```

### Uso Básico

```python
import spacy

# Cargar el modelo de español
nlp = spacy.load("es_core_news_sm")

# Procesar un texto
texto = "Ecdotica analiza textos literarios con inteligencia artificial."
doc = nlp(texto)

# Análisis de tokens
for token in doc:
    print(f"{token.text} - {token.pos_} - {token.dep_}")

# Análisis de entidades
for ent in doc.ents:
    print(f"{ent.text}: {ent.label_}")

# Análisis de dependencias
for token in doc:
    if token.dep_ != "punct":
        print(f"{token.text} <-- {token.dep_} -- {token.head.text}")
```

### Enlaces Útiles

- [Documentación oficial de SpaCy](https://spacy.io/)
- [Guía de SpaCy en español](https://spacy.io/usage/models#languages)
- [Tutorial de análisis con SpaCy](https://spacy.io/usage/spacy-101)

## Instalación y Uso de LanguageTool

LanguageTool es una herramienta de revisión de ortografía y gramática que complementa los análisis de Ecdotica.

### Instalación

```bash
# Instala LanguageTool Python
pip install language-tool-python
```

### Uso Básico

```python
import language_tool_python

# Inicializar LanguageTool para español
tool = language_tool_python.LanguageTool('es-ES')

# Analizar un texto
texto = "Los analisis literarios son muy importantes."
errores = tool.check(texto)

# Mostrar errores y sugerencias
for error in errores:
    print(f"Tipo: {error.category}")
    print(f"Posición: {error.offset} - {error.length}")
    print(f"Mensaje: {error.msg}")
    print(f"Sugerencias: {error.replacements}")
    print()

# Corrección automática
texto_corregido = tool.correct(texto)
print(f"Original: {texto}")
print(f"Corregido: {texto_corregido}")
```

### Configuración Avanzada

```python
# Usar servidor local para mejor rendimiento (opcional)
# Primero, descarga e instala LanguageTool:
# https://languagetool.org/

tool = language_tool_python.LanguageTool('es-ES')

# Desactivar reglas específicas
tool.disable_spellcheck = False
tool.language = 'es-ES'
```

### Enlaces Útiles

- [LanguageTool - Página oficial](https://languagetool.org/)
- [Librería Python - LanguageTool](https://github.com/jmoratilla/languagetool-python)
- [Guía de API](https://languagetool.org/development)

## Normas de Edición APA

Todas las contribuciones de documentación y análisis deben seguir las normas APA (7.ª edición).

### Referencias Principales

#### Citas en el Texto

```markdown
(Paz, 1999, p. 45)

Según Paz (1999), el lenguaje es fundamental.

(García et al., 2020)
```

#### Formato de Referencias Bibliográficas

**Libro:**
```
Apellido, A. (Año). Título del libro. Editorial.
```

**Artículo en revista:**
```
Apellido, A. (Año). Título del artículo. Título de la Revista, volumen(número), páginas. https://doi.org/...
```

**Página web:**
```
Autor, A. (Año). Título de la página. Recuperado de https://www.ejemplo.com
```

**Referencia de software:**
```
SpaCy. (2021). spaCy: Industrial-strength natural language processing. Recuperado de https://spacy.io/
```

### Estructura de Documentos

- **Portada**: Título, autor, institución, fecha
- **Resumen**: 150-250 palabras
- **Palabras clave**: 3-5 términos
- **Introducción**: Contexto y objetivos
- **Desarrollo**: Análisis y hallazgos
- **Conclusiones**: Síntesis de resultados
- **Referencias**: Alfabetizadas, con sangría francesa

### Formato de Texto

- **Fuente**: Times New Roman, 12pt
- **Espaciado**: Doble espaciado
- **Márgenes**: 2.54 cm en todos los lados
- **Alineación**: Justificada
- **Sangría**: 1.27 cm para párrafos

### Enlaces Útiles

- [Manual de Publicaciones APA (7.ª edición)](https://apastyle.apa.org/style-grammar-guidelines)
- [Generador de referencias APA](https://www.mendeley.com/)
- [Guía APA en español](https://www.apa.org/)

## Configuración de Colaboradores

### Añadir Colaboradores al Repositorio

**Pasos en Configuración del Repositorio:**

1. Ve a [Settings](https://github.com/Pazuco/Ecdotica/settings)
2. En el menú izquierdo, selecciona "Collaborators and teams"
3. Haz clic en "Add people"
4. Busca el nombre de usuario del colaborador
5. Selecciona el nivel de permisos:
   - **Pull**: Acceso de lectura
   - **Push**: Acceso de escritura
   - **Admin**: Control total
6. Haz clic en "Add [usuario] to this repository"

### Roles Recomendados por Especialidad

| Especialidad | Género | Rol Sugerido | Permisos |
|-------------|--------|-------------|----------|
| Experto literario | Narrativa | Maintainer | Push |
| Especialista en métrica | Lírica | Contributor | Push |
| Analista sintáctico | Drama | Contributor | Push |
| Revisor de calidad | General | Reviewer | Pull |

### Gestión de Equipos

1. Ve a Settings → Teams
2. Crea equipos por especialidad:
   - `@ecdotica/narrativa`
   - `@ecdotica/lirica`
   - `@ecdotica/drama`
   - `@ecdotica/revisores`
3. Asigna colaboradores a sus equipos
4. Configura permisos de revisión (branch protections)

## Proceso de Revisión

### Criterios de Aceptación para PR

- ✅ Código sigue la guía de estilo del proyecto
- ✅ Includes tests para nuevas funcionalidades
- ✅ Documentación actualizada
- ✅ Sin conflictos con la rama principal
- ✅ Al menos una revisión aprobada
- ✅ Mención de Issues relacionados

### Comunicación

- Usa comentarios descriptivos en el código
- Responde oportunamente a revisiones
- Mantén el tono profesional y colaborativo
- Utiliza la etiqueta `@equipo` para notificaciones

## Recursos Adicionales

- [Documentación del Repositorio](https://github.com/Pazuco/Ecdotica)
- [Issues Abiertos](https://github.com/Pazuco/Ecdotica/issues)
- [Discusiones del Proyecto](https://github.com/Pazuco/Ecdotica/discussions)

---

**Última actualización**: Noviembre 2025

¡Gracias por contribuir a Ecdotica! 🎉
