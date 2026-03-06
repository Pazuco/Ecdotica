# Contribuir al flujo CI/CD de Ecdotica

El proyecto ahora cuenta con integración CI/CD automática usando GitHub Actions.

## ¿Qué verifica el workflow?
- Instalación de dependencias automáticamente.
- Linting con flake8 (estilo de código Python).
- Revisión estática (compilación básica de scripts).
- Pruebas rápidas de análisis NLP con SpaCy y LanguageTool.

## Buenas prácticas para colaborar
1. Antes de hacer un PR, verifica localmente tu código con:
   ```bash
   flake8 src
   ```
2. Siempre que hagas push o PR, tu rama será revisada automáticamente. Si hay errores de flake8, tu contribución aparecerá como 'fallida'.
3. Puedes ver los resultados del workflow en la pestaña 'Actions' de GitHub.
4. Si necesitas agregar dependencias nuevas, házlo en requirements.txt y avisa en el PR.

## Ejemplo de comando para test local
```bash
python -m compileall src
python -c "from procesamiento import nlp; nlp.analizar_texto_ejemplo()" --working-directory=./src
```

¡Gracias por mantener la calidad y automatización del proyecto editorial!
