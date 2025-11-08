class EditorDeTexto:
    def __init__(self):
        self.texto = ''
    def cargar_texto(self, texto):
        '''Carga el texto a editar.'''
        self.texto = texto
    def encontrar_espacios_dobles(self):
        '''Identifica espacios dobles en el texto.'''
        return [i for i in range(len(self.texto)-1) if self.texto[i] == ' ' and self.texto[i+1] == ' ']
    def falta_puntuacion(self):
        '''Detecta líneas que podrían no terminar correctamente con puntuación.'''
        import re
        lineas = self.texto.split('\n')
        return [n for n, l in enumerate(lineas) if l and not re.search(r'[.!?]$', l.strip())]
    def errores_comunes(self):
        '''Detecta errores comunes predefinidos en el texto (puede ampliarse).'''
        errores = {'teh': 'the', 'recivido': 'recibido', 'escribirr': 'escribir'}
        encontrados = {}
        for err in errores:
            if err in self.texto:
                encontrados[err] = errores[err]
        return encontrados
