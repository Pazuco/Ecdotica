# Sistema de Evaluación Automatizada de Manuscritos

## Editorial Nuevo Milenio

Sistema modular para evaluar la aptitud de manuscritos para publicación en Editorial Nuevo Milenio, con criterios específicos para cada género literario.

## Características

- **Modular**: Criterios independientes por género (novela, cuento, poesía, ensayo, crónica)
- - **Automatizado**: Análisis rápido basado en lógica editorial
  - - **Reportes**: Generación automática de reportes con recomendaciones
   
    - ## Estructura del Proyecto
   
    - ```
      src/procesamiento/
      ├── criterios/
      │   ├── __init__.py
      │   ├── novela.py        # Criterios para novelas
      │   └── cuento.py        # Criterios para cuentos
      ├── archivos.py       # Lectura de archivos (PDF, TXT, DOCX)
      ├── utils.py          # Funciones de análisis de texto
      ├── evaluador.py      # Pipeline central
      └── README.md         # Este archivo
      ```

      ## Cómo Usar

      ### Ejecución básica

      ```bash
      python src/procesamiento/evaluador.py <ruta_manuscrito> <genero>
      ```

      ### Ejemplo

      ```bash
      python src/procesamiento/evaluador.py manuscritos/novela.txt novela
      ```

      ## Géneros Soportados

      - **novela**: Entre 30,000 y 150,000 palabras
      - - **cuento**: Entre 1,000 y 30,000 palabras
        - - **poesía**: (En desarrollo)
          - - **ensayo**: (En desarrollo)
            - - **crónica**: (En desarrollo)
             
              - ## Criterios de Evaluación
             
              - Cada género tiene criterios propios:
             
              - - **Ortografía y Gramática**: Límite de errores graves
                - - **Longitud**: Rango de palabras recomendado
                  - - **Estructura**: Requisitos de formato (capítulos, etc.)
                    - - **Legibilidad**: Índice mínimo de facilidad de lectura
                     
                      - ## Instalación de Dependencias
                     
                      - ```bash
                        pip install -r requirements.txt
                        ```

                        ### Dependencias Futuras

                        - **spacy**: Para análisis morfosináctico avan zado
                        - - **language-tool-python**: Para verificación de gramática
                          - - **PyPDF2**: Para lectura de PDF
                            - - **python-docx**: Para lectura de DOCX
