import unittest
import os
from procesamiento import archivos

class TestProcesadorDeArchivos(unittest.TestCase):
    def setUp(self):
        self.procesador = archivos.ProcesadorDeArchivos()
        self.ruta_ejemplo = os.path.join(os.path.dirname(__file__), '../src/samples/sample.txt')
    def test_extraer_txt(self):
        texto = self.procesador._extraer_txt(self.ruta_ejemplo)
        self.assertIn('Amor sin libertad', texto)
        self.assertGreater(len(texto), 100)
if __name__ == '__main__':
    unittest.main()
