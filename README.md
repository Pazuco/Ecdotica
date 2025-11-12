# Ecdotica 2.0

**El primer editor de texto open source especializado en edición crítica digital**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

---

## 📚 Descripción

Ecdotica es una herramienta moderna para la **edición crítica digital**, combinando tecnologías de vanguardia con rigor académico. Diseñada para editores, investigadores y filológos que trabajan con textos literarios e históricos.

### ✨ Características Principales

- **Análisis NLP Avanzado**: Procesamiento de lenguaje natural optimizado para español
- **Colaboración en Tiempo Real**: Edición simultánea entre múltiples usuarios
- **Exportación Universal**: TEI-XML, PDF, HTML5, DOCX, LaTeX
- **Búsqueda Semántica**: Encuentra similitudes y referencias con IA
- **Editor Inteligente**: Auto-completado y sugerencias contextuales
- **Control de Versiones**: Gestión de variantes textuales
- **Géneros Especializados**: Narrativa, Lírica, Drama, Ensayo, Crónica, Crítica

---

## 🚀 Inicio Rápido

### Requisitos Previos

- Docker y Docker Compose
- Python 3.11+
- Git

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/Pazuco/Ecdotica.git
cd Ecdotica

# Iniciar con Docker
docker-compose up -d

# La API estará disponible en:
# http://localhost:8000
# Documentación: http://localhost:8000/api/docs
```

---

## 🏛️ Arquitectura

### Stack Tecnológico

#### Backend
- **FastAPI**: Framework REST moderno y rápido
- **SQLAlchemy 2.0**: ORM para PostgreSQL
- **Pydantic v2**: Validación de datos
- **Redis**: Caché y sesiones
- **SpaCy + LanguageTool**: Análisis NLP

#### Frontend (En desarrollo)
- **PyQt6**: Interfaz gráfica de escritorio
- **QScintilla**: Editor de código avanzado
- **Qt Designer**: Diseño visual

#### DevOps
- **Docker**: Contenedores
- **GitHub Actions**: CI/CD automático
- **PostgreSQL 15**: Base de datos

### Estructura del Proyecto

```
Ecdotica/
├── backend/              # API REST FastAPI
│   ├── main.py          # Aplicación principal
│   ├── models/          # Modelos SQLAlchemy
│   ├── schemas/         # Schemas Pydantic
│   ├── services/        # Lógica de negocio
│   └── routes/          # Endpoints API
├── frontend/             # Interfaz PyQt6 (próximamente)
├── src/                  # Módulos de procesamiento
│   ├── procesamiento/   # NLP y archivos
│   ├── narrativa/       # Reglas de género
│   ├── lirica/
│   ├── drama/
│   └── ...
├── tests/                # Tests automatizados
├── docs/                 # Documentación
├── docker/               # Dockerfiles
├── requirements/         # Dependencias Python
└── docker-compose.yml    # Orquestación
```

---

## 💻 Uso

### API REST

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())
# {"status": "healthy", "service": "ecdotica-api"}

# Info de la API
info = requests.get("http://localhost:8000/api/v1/info")
print(info.json())
```

### Procesamiento de Textos

```python
from src.procesamiento.nlp import AnalizadorNLP

analizador = AnalizadorNLP()
resultado = analizador.analizar_texto("Texto literario...")
print(resultado.estadisticas)
```

---

## 🛠️ Desarrollo

### Configurar Entorno Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements/dev.txt

# Descargar modelo SpaCy
python -m spacy download es_core_news_sm

# Ejecutar tests
pytest tests/

# Linting
flake8 src/ backend/
```

### Variables de Entorno

Crear archivo `.env`:

```env
DATABASE_URL=postgresql://ecdotica_user:password@localhost:5432/ecdotica_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=tu-secret-key-seguro
ENVIRONMENT=development
```

---

## 📝 Documentación

- **[Arquitectura y Roadmap](docs/ARQUITECTURA_Y_ROADMAP.md)**: Plan técnico completo
- **[Guía de Contribución](CONTRIBUTING.md)**: Cómo colaborar
- **[API Docs](http://localhost:8000/api/docs)**: Documentación interactiva

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: amazing feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Lee [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

---

## 📋 Roadmap

### Fase 1: Fundamentos (Completada ✅)
- [x] Arquitectura MVC definida
- [x] Docker Compose configurado
- [x] FastAPI backend base
- [x] Modelos SQLAlchemy
- [x] CI/CD con GitHub Actions

### Fase 2: Funcionalidades Core (En progreso 🔧)
- [ ] API REST completa (CRUD documentos)
- [ ] Integración NLP avanzada
- [ ] Sistema de usuarios y autenticación
- [ ] Interfaz PyQt6 básica

### Fase 3: Características Avanzadas (Planeado 📅)
- [ ] Colaboración tiempo real (WebSockets)
- [ ] Búsqueda semántica con IA
- [ ] Exportadores (TEI-XML, PDF, HTML)
- [ ] Integración cloud (S3/GCS)

### Fase 4: Producción (Planeado 📍)
- [ ] Testing exhaustivo
- [ ] Documentación completa
- [ ] Release 2.0 estable
- [ ] Difusión académica

---

## 🎓 Para Investigadores

Ecdotica está diseñado para:

- **Edición crítica**: Gestión de variantes y aparato crítico
- **Digital Humanities**: Estándares TEI-XML
- **Análisis filológico**: Herramientas NLP especializadas
- **Investigación colaborativa**: Control de versiones y comentarios

---

## 📜 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

---

## 📧 Contacto

**Editorial Nuevo Milenio**
- Repositorio: [https://github.com/Pazuco/Ecdotica](https://github.com/Pazuco/Ecdotica)
- Issues: [https://github.com/Pazuco/Ecdotica/issues](https://github.com/Pazuco/Ecdotica/issues)

---

**Ecdotica 2.0** - Modernizando la edición crítica para el siglo XXI
