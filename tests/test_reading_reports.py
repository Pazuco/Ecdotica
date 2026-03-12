"""Tests para el módulo de Informes de Lectura.

Incluye tests unitarios para modelos Pydantic, generación de prompts,
y tests de integración para los endpoints de la API.
"""

import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Agregar raíz del proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.models.reading_reports import (
    EstadoTrabajo,
    FichaBibliografica,
    FormatoInforme,
    InformeLecturaCompleto,
    RespuestaInformeCompleto,
    RespuestaTrabajo,
    SolicitudInformeLectura,
)
from api.prompts.reading_reports import (
    INSTRUCCIONES_FORMATO,
    LONGITUDES_FORMATO,
    construir_prompt_informe,
)


# ═══════════════════════════════════════════════════════════════
# Tests de Modelos Pydantic
# ═══════════════════════════════════════════════════════════════


class TestFormatoInforme:
    """Tests para el enum FormatoInforme."""

    def test_valores_disponibles(self):
        assert FormatoInforme.BREVE == "breve"
        assert FormatoInforme.ESTANDAR == "estandar"
        assert FormatoInforme.DETALLADO == "detallado"

    def test_total_formatos(self):
        assert len(FormatoInforme) == 3


class TestSolicitudInformeLectura:
    """Tests para el modelo de solicitud de informe."""

    def test_solicitud_minima_valida(self):
        solicitud = SolicitudInformeLectura(
            titulo_libro="Cien años de soledad",
            autor="Gabriel García Márquez",
            email_usuario="test@ejemplo.com",
        )
        assert solicitud.titulo_libro == "Cien años de soledad"
        assert solicitud.autor == "Gabriel García Márquez"
        assert solicitud.formato == FormatoInforme.ESTANDAR
        assert solicitud.genero is None
        assert solicitud.notas_usuario is None

    def test_solicitud_completa(self):
        solicitud = SolicitudInformeLectura(
            titulo_libro="Pedro Páramo",
            autor="Juan Rulfo",
            genero="Novela",
            notas_usuario="Enfoque en el realismo mágico",
            formato=FormatoInforme.DETALLADO,
            email_usuario="lector@ecdotica.com",
        )
        assert solicitud.genero == "Novela"
        assert solicitud.formato == FormatoInforme.DETALLADO
        assert solicitud.notas_usuario == "Enfoque en el realismo mágico"

    def test_titulo_vacio_falla(self):
        with pytest.raises(Exception):
            SolicitudInformeLectura(
                titulo_libro="",
                autor="Autor",
                email_usuario="test@ejemplo.com",
            )

    def test_titulo_solo_espacios_falla(self):
        with pytest.raises(Exception):
            SolicitudInformeLectura(
                titulo_libro="   ",
                autor="Autor",
                email_usuario="test@ejemplo.com",
            )

    def test_autor_vacio_falla(self):
        with pytest.raises(Exception):
            SolicitudInformeLectura(
                titulo_libro="Libro",
                autor="",
                email_usuario="test@ejemplo.com",
            )

    def test_email_invalido_falla(self):
        with pytest.raises(Exception):
            SolicitudInformeLectura(
                titulo_libro="Libro",
                autor="Autor",
                email_usuario="no-es-email",
            )

    def test_titulo_se_recorta(self):
        solicitud = SolicitudInformeLectura(
            titulo_libro="  El túnel  ",
            autor="  Ernesto Sabato  ",
            email_usuario="test@ejemplo.com",
        )
        assert solicitud.titulo_libro == "El túnel"
        assert solicitud.autor == "Ernesto Sabato"

    def test_notas_largo_maximo(self):
        notas_largas = "a" * 2000
        solicitud = SolicitudInformeLectura(
            titulo_libro="Libro",
            autor="Autor",
            email_usuario="test@ejemplo.com",
            notas_usuario=notas_largas,
        )
        assert len(solicitud.notas_usuario) == 2000

    def test_notas_excede_maximo_falla(self):
        with pytest.raises(Exception):
            SolicitudInformeLectura(
                titulo_libro="Libro",
                autor="Autor",
                email_usuario="test@ejemplo.com",
                notas_usuario="a" * 2001,
            )


class TestEstadoTrabajo:
    """Tests para el enum EstadoTrabajo."""

    def test_estados_disponibles(self):
        assert EstadoTrabajo.PENDIENTE == "pendiente"
        assert EstadoTrabajo.PROCESANDO == "procesando"
        assert EstadoTrabajo.COMPLETADO == "completado"
        assert EstadoTrabajo.FALLIDO == "fallido"


class TestRespuestaTrabajo:
    """Tests para el modelo de respuesta de trabajo."""

    def test_respuesta_basica(self):
        respuesta = RespuestaTrabajo(
            trabajo_id="abc-123",
            estado=EstadoTrabajo.PENDIENTE,
        )
        assert respuesta.trabajo_id == "abc-123"
        assert respuesta.estado == EstadoTrabajo.PENDIENTE
        assert respuesta.progreso == 0
        assert respuesta.fecha_completado is None

    def test_respuesta_con_progreso(self):
        respuesta = RespuestaTrabajo(
            trabajo_id="abc-123",
            estado=EstadoTrabajo.PROCESANDO,
            progreso=50,
            mensaje="Generando análisis temático...",
        )
        assert respuesta.progreso == 50
        assert respuesta.mensaje == "Generando análisis temático..."

    def test_progreso_fuera_de_rango_falla(self):
        with pytest.raises(Exception):
            RespuestaTrabajo(
                trabajo_id="abc-123",
                estado=EstadoTrabajo.PROCESANDO,
                progreso=150,
            )


class TestFichaBibliografica:
    """Tests para el modelo de ficha bibliográfica."""

    def test_ficha_minima(self):
        ficha = FichaBibliografica(
            titulo="Rayuela",
            autor="Julio Cortázar",
        )
        assert ficha.titulo == "Rayuela"
        assert ficha.idioma == "Español"
        assert ficha.editorial is None

    def test_ficha_completa(self):
        ficha = FichaBibliografica(
            titulo="Rayuela",
            autor="Julio Cortázar",
            genero="Novela",
            anio_publicacion="1963",
            editorial="Sudamericana",
            idioma="Español",
            paginas_estimadas="600",
        )
        assert ficha.anio_publicacion == "1963"
        assert ficha.editorial == "Sudamericana"


class TestInformeLecturaCompleto:
    """Tests para el modelo de informe completo."""

    @pytest.fixture
    def informe_datos(self):
        return {
            "ficha_bibliografica": FichaBibliografica(
                titulo="El Aleph",
                autor="Jorge Luis Borges",
                genero="Cuento",
            ),
            "sinopsis": "Colección de cuentos fantásticos...",
            "analisis_tematico": "Los temas principales incluyen...",
            "analisis_estilo_estructura": "Borges emplea un estilo...",
            "contexto_literario": "Publicado en 1949...",
            "valoracion_critica": "Una obra maestra de la literatura...",
            "publico_recomendado": "Lectores de literatura fantástica...",
            "calificacion": 5,
            "justificacion_calificacion": "Obra cumbre de la narrativa breve...",
        }

    def test_informe_valido(self, informe_datos):
        informe = InformeLecturaCompleto(**informe_datos)
        assert informe.calificacion == 5
        assert informe.ficha_bibliografica.titulo == "El Aleph"

    def test_calificacion_fuera_de_rango_falla(self, informe_datos):
        informe_datos["calificacion"] = 0
        with pytest.raises(Exception):
            InformeLecturaCompleto(**informe_datos)

        informe_datos["calificacion"] = 6
        with pytest.raises(Exception):
            InformeLecturaCompleto(**informe_datos)

    def test_calificacion_valida_rango(self, informe_datos):
        for cal in range(1, 6):
            informe_datos["calificacion"] = cal
            informe = InformeLecturaCompleto(**informe_datos)
            assert informe.calificacion == cal


# ═══════════════════════════════════════════════════════════════
# Tests de Prompts
# ═══════════════════════════════════════════════════════════════


class TestConstruirPromptInforme:
    """Tests para la función de construcción de prompts."""

    def test_prompt_basico(self):
        sistema, usuario = construir_prompt_informe(
            titulo="Don Quijote de la Mancha",
            autor="Miguel de Cervantes",
        )
        assert "crítico literario" in sistema.lower()
        assert "Don Quijote de la Mancha" in usuario
        assert "Miguel de Cervantes" in usuario
        assert "JSON" in sistema

    def test_prompt_con_genero(self):
        _, usuario = construir_prompt_informe(
            titulo="Libro",
            autor="Autor",
            genero="Novela",
        )
        assert "Novela" in usuario

    def test_prompt_sin_genero(self):
        _, usuario = construir_prompt_informe(
            titulo="Libro",
            autor="Autor",
            genero=None,
        )
        assert "No especificado" in usuario

    def test_prompt_con_notas(self):
        _, usuario = construir_prompt_informe(
            titulo="Libro",
            autor="Autor",
            notas_usuario="Analizar el uso de metáforas",
        )
        assert "Analizar el uso de metáforas" in usuario

    def test_prompt_formato_breve(self):
        _, usuario = construir_prompt_informe(
            titulo="Libro",
            autor="Autor",
            formato=FormatoInforme.BREVE,
        )
        assert "500 palabras" in usuario
        assert "conciso" in usuario.lower() or "Sé conciso" in usuario

    def test_prompt_formato_detallado(self):
        _, usuario = construir_prompt_informe(
            titulo="Libro",
            autor="Autor",
            formato=FormatoInforme.DETALLADO,
        )
        assert "3000 palabras" in usuario
        assert "exhaustivo" in usuario.lower() or "académico" in usuario.lower()

    def test_todos_formatos_tienen_longitud(self):
        for formato in FormatoInforme:
            assert formato in LONGITUDES_FORMATO

    def test_todos_formatos_tienen_instrucciones(self):
        for formato in FormatoInforme:
            assert formato in INSTRUCCIONES_FORMATO

    def test_prompt_sistema_es_string(self):
        sistema, usuario = construir_prompt_informe(
            titulo="Libro",
            autor="Autor",
        )
        assert isinstance(sistema, str)
        assert isinstance(usuario, str)
        assert len(sistema) > 100
        assert len(usuario) > 50


# ═══════════════════════════════════════════════════════════════
# Tests de Integración (Endpoints API)
# ═══════════════════════════════════════════════════════════════


class TestEndpointsAPI:
    """Tests de integración para los endpoints de la API.

    Estos tests usan FastAPI TestClient y mockean la API de OpenAI.
    Para ejecutarlos se necesitan las dependencias: fastapi, httpx.
    """

    @pytest.fixture
    def cliente_test(self):
        """Crea un cliente de prueba para la API."""
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            from api.routers.reading_reports import router

            app = FastAPI()
            app.include_router(router)
            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI o httpx no disponibles para tests de integración")

    def test_crear_informe_solicitud_valida(self, cliente_test):
        """Test que una solicitud válida devuelve 202 con trabajo_id."""
        with patch("api.services.report_generator.GeneradorInformes._procesar_informe"):
            respuesta = cliente_test.post(
                "/api/v1/informes-lectura",
                json={
                    "titulo_libro": "Cien años de soledad",
                    "autor": "Gabriel García Márquez",
                    "formato": "estandar",
                    "email_usuario": "test@ejemplo.com",
                },
            )
        assert respuesta.status_code == 202
        datos = respuesta.json()
        assert "trabajo_id" in datos
        assert datos["estado"] == "pendiente"

    def test_crear_informe_sin_titulo_falla(self, cliente_test):
        """Test que una solicitud sin título devuelve error de validación."""
        respuesta = cliente_test.post(
            "/api/v1/informes-lectura",
            json={
                "autor": "Autor",
                "email_usuario": "test@ejemplo.com",
            },
        )
        assert respuesta.status_code == 422

    def test_crear_informe_email_invalido_falla(self, cliente_test):
        """Test que un email inválido devuelve error de validación."""
        respuesta = cliente_test.post(
            "/api/v1/informes-lectura",
            json={
                "titulo_libro": "Libro",
                "autor": "Autor",
                "email_usuario": "no-email",
            },
        )
        assert respuesta.status_code == 422

    def test_consultar_trabajo_inexistente(self, cliente_test):
        """Test que consultar un trabajo inexistente devuelve 404."""
        respuesta = cliente_test.get(
            "/api/v1/informes-lectura/id-inexistente-999"
        )
        assert respuesta.status_code == 404

    def test_obtener_informe_trabajo_inexistente(self, cliente_test):
        """Test que obtener un informe inexistente devuelve 404."""
        respuesta = cliente_test.get(
            "/api/v1/informes-lectura/id-inexistente-999/report"
        )
        assert respuesta.status_code == 404

    def test_obtener_informe_no_completado(self, cliente_test):
        """Test que obtener un informe no completado devuelve 409."""
        with patch("api.services.report_generator.GeneradorInformes._procesar_informe"):
            resp_crear = cliente_test.post(
                "/api/v1/informes-lectura",
                json={
                    "titulo_libro": "Libro Test",
                    "autor": "Autor Test",
                    "email_usuario": "test@ejemplo.com",
                },
            )
        trabajo_id = resp_crear.json()["trabajo_id"]

        respuesta = cliente_test.get(
            f"/api/v1/informes-lectura/{trabajo_id}/report"
        )
        assert respuesta.status_code == 409

    def test_consultar_estado_trabajo_existente(self, cliente_test):
        """Test que consultar un trabajo existente devuelve su estado."""
        with patch("api.services.report_generator.GeneradorInformes._procesar_informe"):
            resp_crear = cliente_test.post(
                "/api/v1/informes-lectura",
                json={
                    "titulo_libro": "La ciudad y los perros",
                    "autor": "Mario Vargas Llosa",
                    "genero": "Novela",
                    "email_usuario": "mvll@ejemplo.com",
                },
            )
        trabajo_id = resp_crear.json()["trabajo_id"]

        respuesta = cliente_test.get(
            f"/api/v1/informes-lectura/{trabajo_id}"
        )
        assert respuesta.status_code == 200
        datos = respuesta.json()
        assert datos["trabajo_id"] == trabajo_id
