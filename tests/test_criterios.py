"""
Tests para los módulos de criterios editoriales de todos los géneros.
"""

import pytest
from criterios import novela, cuento, poema, ensayo, cronica


# ---------------------------------------------------------------------------
# Fixtures de stats reutilizables
# ---------------------------------------------------------------------------

@pytest.fixture
def stats_novela_apta():
    return {'num_palabras': 60000, 'num_capitulos': 5, 'indice_legibilidad': 65, 'errores_graves': 2}

@pytest.fixture
def stats_cuento_apto():
    return {'num_palabras': 8000, 'num_capitulos': 0, 'indice_legibilidad': 70, 'errores_graves': 1}

@pytest.fixture
def stats_poema_apto():
    return {'num_palabras': 120, 'num_capitulos': 0, 'indice_legibilidad': 50, 'errores_graves': 0}

@pytest.fixture
def stats_ensayo_apto():
    return {'num_palabras': 5000, 'num_capitulos': 0, 'indice_legibilidad': 55, 'errores_graves': 0}

@pytest.fixture
def stats_cronica_apta():
    return {'num_palabras': 2500, 'num_capitulos': 0, 'indice_legibilidad': 65, 'errores_graves': 1}


# ---------------------------------------------------------------------------
# Novela
# ---------------------------------------------------------------------------

class TestNovela:
    def test_manuscrito_apto(self, stats_novela_apta):
        resultados = novela.evaluar_novela(stats_novela_apta)
        assert all(v['cumple'] for v in resultados.values())

    def test_longitud_minima(self):
        stats = {'num_palabras': 1000}
        resultado = novela.evaluar_longitud(stats)
        assert resultado['cumple'] is False

    def test_longitud_maxima(self):
        stats = {'num_palabras': 200000}
        resultado = novela.evaluar_longitud(stats)
        assert resultado['cumple'] is False

    def test_longitud_correcta(self):
        stats = {'num_palabras': 80000}
        resultado = novela.evaluar_longitud(stats)
        assert resultado['cumple'] is True

    def test_estructura_requiere_3_capitulos(self):
        assert novela.evaluar_estructura({'num_capitulos': 2})['cumple'] is False
        assert novela.evaluar_estructura({'num_capitulos': 3})['cumple'] is True

    def test_legibilidad_minima(self):
        assert novela.evaluar_legibilidad({'indice_legibilidad': 49})['cumple'] is False
        assert novela.evaluar_legibilidad({'indice_legibilidad': 50})['cumple'] is True

    def test_devuelve_cuatro_criterios(self, stats_novela_apta):
        resultados = novela.evaluar_novela(stats_novela_apta)
        assert set(resultados.keys()) == {'ortografia_gramatica', 'longitud', 'estructura', 'legibilidad'}


# ---------------------------------------------------------------------------
# Cuento
# ---------------------------------------------------------------------------

class TestCuento:
    def test_manuscrito_apto(self, stats_cuento_apto):
        resultados = cuento.evaluar_cuento(stats_cuento_apto)
        assert all(v['cumple'] for v in resultados.values())

    def test_longitud_minima(self):
        stats = {'num_palabras': 500}
        resultado = cuento.evaluar_longitud(stats)
        assert resultado['cumple'] is False

    def test_longitud_correcta(self):
        stats = {'num_palabras': 5000}
        resultado = cuento.evaluar_longitud(stats)
        assert resultado['cumple'] is True

    def test_estructura_siempre_cumple(self):
        assert cuento.evaluar_estructura({})['cumple'] is True

    def test_legibilidad_minima(self):
        assert cuento.evaluar_legibilidad({'indice_legibilidad': 59})['cumple'] is False
        assert cuento.evaluar_legibilidad({'indice_legibilidad': 60})['cumple'] is True


# ---------------------------------------------------------------------------
# Poema
# ---------------------------------------------------------------------------

class TestPoema:
    def test_manuscrito_apto(self, stats_poema_apto):
        resultados = poema.evaluar_poema(stats_poema_apto)
        assert all(v['cumple'] for v in resultados.values())

    def test_longitud_minima(self):
        stats = {'num_palabras': 3}
        resultado = poema.evaluar_longitud(stats)
        assert resultado['cumple'] is False

    def test_longitud_maxima(self):
        stats = {'num_palabras': 3000}
        resultado = poema.evaluar_longitud(stats)
        assert resultado['cumple'] is False

    def test_longitud_correcta(self):
        stats = {'num_palabras': 80}
        resultado = poema.evaluar_longitud(stats)
        assert resultado['cumple'] is True

    def test_estructura_siempre_cumple(self):
        assert poema.evaluar_estructura({})['cumple'] is True

    def test_legibilidad_admite_complejidad(self):
        # El poema tiene umbral bajo (30), admite mayor complejidad
        assert poema.evaluar_legibilidad({'indice_legibilidad': 29})['cumple'] is False
        assert poema.evaluar_legibilidad({'indice_legibilidad': 30})['cumple'] is True


# ---------------------------------------------------------------------------
# Ensayo
# ---------------------------------------------------------------------------

class TestEnsayo:
    def test_manuscrito_apto(self, stats_ensayo_apto):
        resultados = ensayo.evaluar_ensayo(stats_ensayo_apto)
        assert all(v['cumple'] for v in resultados.values())

    def test_longitud_minima(self):
        stats = {'num_palabras': 500}
        resultado = ensayo.evaluar_longitud(stats)
        assert resultado['cumple'] is False

    def test_longitud_correcta(self):
        stats = {'num_palabras': 10000}
        resultado = ensayo.evaluar_longitud(stats)
        assert resultado['cumple'] is True

    def test_estructura_siempre_cumple(self):
        assert ensayo.evaluar_estructura({})['cumple'] is True

    def test_umbral_error_estricto(self):
        # Ensayo: < 3 errores por 10,000 palabras
        stats = {'errores_graves': 4, 'num_palabras': 10000}
        resultado = ensayo.evaluar_ortografia_gramatica(stats)
        assert resultado['cumple'] is False

    def test_legibilidad_minima(self):
        assert ensayo.evaluar_legibilidad({'indice_legibilidad': 39})['cumple'] is False
        assert ensayo.evaluar_legibilidad({'indice_legibilidad': 40})['cumple'] is True


# ---------------------------------------------------------------------------
# Crónica
# ---------------------------------------------------------------------------

class TestCronica:
    def test_manuscrito_apto(self, stats_cronica_apta):
        resultados = cronica.evaluar_cronica(stats_cronica_apta)
        assert all(v['cumple'] for v in resultados.values())

    def test_longitud_minima(self):
        stats = {'num_palabras': 200}
        resultado = cronica.evaluar_longitud(stats)
        assert resultado['cumple'] is False

    def test_longitud_maxima(self):
        stats = {'num_palabras': 20000}
        resultado = cronica.evaluar_longitud(stats)
        assert resultado['cumple'] is False

    def test_longitud_correcta(self):
        stats = {'num_palabras': 3000}
        resultado = cronica.evaluar_longitud(stats)
        assert resultado['cumple'] is True

    def test_estructura_siempre_cumple(self):
        assert cronica.evaluar_estructura({})['cumple'] is True

    def test_legibilidad_minima(self):
        assert cronica.evaluar_legibilidad({'indice_legibilidad': 54})['cumple'] is False
        assert cronica.evaluar_legibilidad({'indice_legibilidad': 55})['cumple'] is True
