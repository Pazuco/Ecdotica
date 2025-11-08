import spacy
import language_tool_python
import os

def analizar_texto_ejemplo():
    """Ejemplo de análisis usando SpaCy y LanguageTool."""
    print("Cargando modelo de SpaCy para español...")
    nlp = spacy.load("es_core_news_sm")
    print("Inicializando LanguageTool...")
    tool = language_tool_python.LanguageTool('es')
    ruta_sample = os.path.join(os.path.dirname(__file__), '..', 'samples', 'sample.txt')
    try:
        with open(ruta_sample, 'r', encoding='utf-8') as f:
            texto = f.read()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta_sample}")
        return
    primer_parrafo = texto.split('\n\n')[1] if '\n\n' in texto else texto[:500]
    doc = nlp(primer_parrafo)
    print("\n1. ENTIDADES NOMBRADAS:")
    if doc.ents:
        for ent in doc.ents:
            print(f"  - {ent.text:20} | Tipo: {ent.label_:10} | {spacy.explain(ent.label_)}")
    print("\n2. TOKEN ANALYSIS:")
    for token in list(doc)[:10]:
        print(f"  {token.text:15} | {token.lemma_:15} | {token.pos_:8} | {token.tag_:8} | {token.dep_:10}")
    print("\n3. ORACIONES:")
    oraciones = list(doc.sents)
    print(f"  Total oraciones: {len(oraciones)}")
    if len(oraciones) > 0:
        print(f"  Primera oración: {oraciones[0].text[:100]}...")
    print("\n4. SUSTANTIVOS y VERBOS:")
    print(f"  Sustantivos: {', '.join([t.text for t in doc if t.pos_ == 'NOUN'])}")
    print(f"  Verbos: {', '.join([t.text for t in doc if t.pos_ == 'VERB'])}")
    fragmento_lt = '. '.join(primer_parrafo.split('.')[:3]) + '.'
    matches = tool.check(fragmento_lt)
    print("\n5. SUGERENCIAS DE CORRECCIÓN:")
    for i, match in enumerate(matches[:5], 1):
        print(f"  {i}. Posición {match.offset}-{match.offset + match.errorLength} | Mensaje: {match.message}")
        if match.replacements:
            print(f"     Sugerencias: {', '.join(match.replacements[:3])}")
    tool.close()
    print("\nAnálisis completado.")

def obtener_estadisticas_texto(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            texto = f.read()
        nlp = spacy.load("es_core_news_sm")
        doc = nlp(texto)
        return {
            'caracteres': len(texto),
            'palabras': len([token for token in doc if not token.is_space]),
            'oraciones': len(list(doc.sents)),
            'tokens': len(doc),
            'entidades': len(doc.ents)
        }
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return None
