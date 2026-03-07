"""
Benchmark de precisión métrica para poema/reglas.py.
Editorial Nuevo Milenio

Evalúa la exactitud del conteo silábico comparando contra versos canónicos
de la poesía española con métrica conocida (endecasílabos, octosílabos,
heptasílabos, alejandrinos y versos de arte menor).

Ejecutar directamente:
    python tests/benchmark_metrica.py

No forma parte de la suite pytest — es una herramienta de diagnóstico.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'procesamiento'))

from poema.reglas import contar_silabas

# ---------------------------------------------------------------------------
# Corpus de referencia: (verso, sílabas_esperadas, autor)
# Fuente: métrica canónica de la poesía española clásica y moderna.
# ---------------------------------------------------------------------------

CORPUS = [
    # Endecasílabos (11 sílabas) — metro heroico español
    ("Vuelve hacia atrás la vista, caminante", 11, "Machado"),
    ("Yo quiero ser llorando el hortelano", 11, "Miguel Hernández"),
    ("Nuestras vidas son los ríos", 8, "Jorge Manrique"),
    ("que van a dar en la mar", 7, "Jorge Manrique"),
    ("que es el morir", 4, "Jorge Manrique"),

    # Octosílabos (8 sílabas) — metro del romance
    ("En el principio estaba el Verbo", 8, "Juan de la Cruz"),
    ("Por las orillas del río", 8, "Romance anónimo"),
    ("Con diez cañones por banda", 8, "Espronceda"),
    ("viento en popa a toda vela", 8, "Espronceda"),
    ("no corta el mar, sino vuela", 8, "Espronceda"),

    # Endecasílabos clásicos
    ("Cuando me paro a contemplar mi estado", 11, "Garcilaso"),
    ("a que amé tanto, es tarde ya, poeta", 11, "Bécquer"),
    ("Del salón en el ángulo oscuro", 10, "Bécquer"),

    # Alejandrinos (14 sílabas) — verso modernista
    ("Yo soy aquel que ayer no más decía", 11, "Darío"),
    ("En el país de sueño, de música y de luna", 14, "Darío"),

    # Heptasílabos (7 sílabas)
    ("Volverán las oscuras", 7, "Bécquer"),
    ("golondrinas del amor", 7, "Bécquer"),

    # Versos breves (arte menor)
    ("Alma, ¿qué quieres?", 5, "San Juan de la Cruz"),
    ("Verde que te quiero verde", 8, "Lorca"),
    ("verde viento, verdes ramas", 8, "Lorca"),
    ("el barco sobre la mar", 7, "Lorca"),
    ("y el caballo en la montaña", 8, "Lorca"),

    # Versos modernos
    ("A las cinco de la tarde", 8, "Lorca"),
    ("Eran las cinco en punto de la tarde", 11, "Lorca"),
    ("Un niño trajo la blanca sábana", 10, "Lorca"),
    ("a las cinco de la tarde", 8, "Lorca"),

    # Soneto de Quevedo — endecasílabos
    ("Miré los muros de la patria mía", 11, "Quevedo"),
    ("si un tiempo fuertes, ya desmoronados", 11, "Quevedo"),
]

# ---------------------------------------------------------------------------
# Ejecución del benchmark
# ---------------------------------------------------------------------------

def ejecutar_benchmark():
    total = len(CORPUS)
    aciertos_exactos = 0
    aciertos_tolerancia_1 = 0
    errores = []

    print("=" * 65)
    print("BENCHMARK DE PRECISIÓN MÉTRICA — Ecdotica / poema/reglas.py")
    print("=" * 65)
    print(f"{'VERSO':<42} {'ESP':>4} {'OBT':>4} {'DIF':>4}  AUTOR")
    print("-" * 65)

    for verso, esperado, autor in CORPUS:
        obtenido = contar_silabas(verso)
        diferencia = obtenido - esperado
        exacto = diferencia == 0
        cerca = abs(diferencia) <= 1

        if exacto:
            aciertos_exactos += 1
        if cerca:
            aciertos_tolerancia_1 += 1
        else:
            errores.append((verso, esperado, obtenido, autor))

        signo = '✓' if exacto else ('~' if cerca else '✗')
        verso_corto = (verso[:39] + '…') if len(verso) > 40 else verso
        print(f"{signo} {verso_corto:<41} {esperado:>4} {obtenido:>4} {diferencia:>+4}  {autor}")

    print("-" * 65)
    precision_exacta = aciertos_exactos / total * 100
    precision_tolerada = aciertos_tolerancia_1 / total * 100

    print(f"\nRESULTADOS:")
    print(f"  Total de versos evaluados : {total}")
    print(f"  Aciertos exactos          : {aciertos_exactos}/{total} ({precision_exacta:.1f}%)")
    print(f"  Aciertos ±1 sílaba        : {aciertos_tolerancia_1}/{total} ({precision_tolerada:.1f}%)")
    print(f"  Errores > ±1 sílaba       : {total - aciertos_tolerancia_1}")

    if errores:
        print(f"\nVERSOS CON ERROR > ±1 SÍLABA:")
        for verso, esp, obt, autor in errores:
            verso_corto = (verso[:45] + '…') if len(verso) > 46 else verso
            print(f"  [{autor}] {verso_corto!r}")
            print(f"    Esperado: {esp}  Obtenido: {obt}  Diferencia: {obt - esp:+d}")

    print("\nNOTA: El conteo silábico aplica sinalefa (aproximación regex).")
    print("      Casos complejos (hiato, diéresis, licencias poéticas)")
    print("      requieren análisis fonológico avanzado para mayor precisión.")
    print("=" * 65)

    return precision_exacta, precision_tolerada


if __name__ == '__main__':
    precision_exacta, precision_tolerada = ejecutar_benchmark()
    # Código de salida no-cero si la precisión exacta baja del 40%
    sys.exit(0 if precision_exacta >= 40 else 1)
