import os

class ProcesadorDeArchivos:
    """
    Procesador central para archivos PDF, TXT y DOCX.
    """
    def extraer_texto(self, ruta):
        ext = os.path.splitext(ruta)[1].lower()
        if ext == '.pdf':
            return self._extraer_pdf(ruta)
        elif ext == '.docx':
            return self._extraer_docx(ruta)
        elif ext == '.txt':
            return self._extraer_txt(ruta)
        else:
            raise ValueError("Tipo de archivo no soportado")

    def _extraer_pdf(self, ruta):
        texto = ""
        try:
            import PyPDF2
            with open(ruta, 'rb') as f:
                lector = PyPDF2.PdfReader(f)
                for pagina in lector.pages:
                    texto += pagina.extract_text() or ""
        except ImportError:
            texto = "PyPDF2 no instalado"
        return texto

    def _extraer_docx(self, ruta):
        texto = ""
        try:
            import docx
            doc = docx.Document(ruta)
            for parrafo in doc.paragraphs:
                texto += parrafo.text + "\n"
        except ImportError:
            texto = "python-docx no instalado"
        return texto

    def _extraer_txt(self, ruta):
        with open(ruta, encoding="utf-8") as f:
            return f.read()
