# Analizador básico de crítica literaria

class AnalizadorCritica:
    """
    Clase base para análisis de reseñas y textos críticos.
    """
    def __init__(self, texto):
        self.texto = texto
    def resumen_critico(self):
        """
        Devuelve las primeras líneas como 'resumen' (ejemplo a expandir).
        """
        return '\n'.join(self.texto.splitlines()[:3])
    def referencias_bibliograficas(self):
        """
        Busca posibles citas APA.
        """
        import re
        return re.findall(r"\([A-Z][a-z]+, [0-9]{4}\)", self.texto)
