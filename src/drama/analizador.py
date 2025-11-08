# Analizador básico para obras dramáticas

class AnalizadorDrama:
    """
    Clase base para análisis preliminar de textos dramáticos.
    """
    def __init__(self, texto):
        self.texto = texto
    def buscar_actos(self):
        """
        Busca divisiones 'Acto' en la obra (puede mejorar detección).
        """
        return [linea for linea in self.texto.splitlines() if 'ACTO' in linea.upper()]
    def buscar_personajes(self):
        """
        Busca nombres de personajes basados en formato habitual de diálogos.
        """
        import re
        return list(set(re.findall(r'^([A-ZÁÉÍÓÚÑ]{2,})\s*:', self.texto, re.MULTILINE)))
