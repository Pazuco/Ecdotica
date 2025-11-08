# Reglas específicas para el procesamiento de cuentos

"""
Este módulo contiene las reglas específicas para el análisis y edición de cuentos.

Las reglas pueden incluir:
- Validación de estructura narrativa (inicio, desarrollo, clímax, desenlace)
- Reglas de estilo específicas del género cuentistico
- Control de extensión y concisión narrativa
- Análisis de impacto y efectividad del final
- Coherencia temática y unidad de efecto

Ejemplo de cómo agregar una regla:

def validar_unidad_temporal(texto):
    """
    Valida que el cuento mantenga unidad temporal adecuada.
    """
    # Implementar lógica de validación
    pass

class ReglaCuentistica:
    def __init__(self, nombre, descripcion, funcion_validacion):
        self.nombre = nombre
        self.descripcion = descripcion
        self.funcion_validacion = funcion_validacion
    
    def aplicar(self, texto):
        return self.funcion_validacion(texto)
"""
