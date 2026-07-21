"""Añade ejercicios nuevos a la biblioteca sin regenerar todo el catálogo.

Reutiliza el motor de animación de build_gifs.py (C, M y save_gif), renderiza
los GIF de los nuevos ejercicios, los convierte a WebP y los inserta en
ejercicios.json/csv, index.html y data.js. Después conviene ejecutar
build_plans.py para que los planes incorporen los nuevos ejercicios.

Uso: OUTPUT_DIR=. python3 scripts/build_extra.py
"""
import os
import re
import json
import csv
import html as htmlmod
import unicodedata
from pathlib import Path

from PIL import Image, ImageFile

import build_gifs as engine  # importar no genera nada (motor sin efectos)

ImageFile.LOAD_TRUNCATED_IMAGES = True
ROOT = Path(os.environ.get('OUTPUT_DIR', '.'))

# Ejercicios avanzados nuevos. La geometría/animación vive en build_gifs.C/M.
NUEVOS = [
    dict(id='IND-21', nombre='Regate en zigzag agresivo', jugadores=1, objetivo='regate', nivel='avanzado', duracion_min=12,
         material='5 conos, 1 balón', diagram='ind21regate',
         instrucciones='Ataca cada cono con una finta de cuerpo y recorta con el exterior al lado contrario, saliendo a máxima velocidad.'),
    dict(id='IND-22', nombre='Protección 360° y salida', jugadores=1, objetivo='protección', nivel='avanzado', duracion_min=10,
         material='3 conos, 1 balón', diagram='ind22shield',
         instrucciones='Protege el balón girando alrededor del cono central, cambia de perfil y sal en conducción hacia una salida distinta cada vez.'),
    dict(id='IND-23', nombre='Decisión por colores', jugadores=1, objetivo='reacción', nivel='avanzado', duracion_min=10,
         material='4 conos de colores, 1 balón', diagram='ind23decide',
         instrucciones='Conduce al centro, levanta la cabeza y sal hacia el color indicado, orientando el control antes de acelerar.'),
    dict(id='PAR-21', nombre='Conducción en espejo con cambios', jugadores=2, objetivo='conducción', nivel='avanzado', duracion_min=10,
         material='8 conos, 2 balones', diagram='par21mirror2',
         instrucciones='Uno marca cambios de dirección y de ritmo dentro de su zona y el otro los replica al instante. Cambiad de líder cada 40 segundos.'),
    dict(id='PAR-22', nombre='Ruptura, apoyo y descarga', jugadores=2, objetivo='desmarque', nivel='avanzado', duracion_min=12,
         material='4 conos, 1 balón', diagram='par22break',
         instrucciones='B rompe al espacio y recibe de cara; descarga al apoyo de A, que llega desde atrás para el pase final.'),
    dict(id='PAR-23', nombre='Transición y decisión', jugadores=2, objetivo='reacción', nivel='avanzado', duracion_min=10,
         material='6 conos, 1 balón', diagram='par23decide',
         instrucciones='A pasa y B decide según la puerta que se abra: devuelve de primeras o gira y sale por el lado contrario.'),
]


def slug(text):
    text = unicodedata.normalize('NFD', text.lower())
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')


def to_webp(gif_path, webp_path):
    image = Image.open(gif_path)
    frames, durations = [], []
    try:
        while True:
            frames.append(image.convert('RGB').copy())
            durations.append(image.info.get('duration', 85))
            image.seek(image.tell() + 1)
    except EOFError:
        pass
    frames[0].save(webp_path, save_all=True, append_images=frames[1:], duration=durations, loop=0, quality=70, method=6)


def main():
    (ROOT / 'gif').mkdir(exist_ok=True)
    (ROOT / 'webp').mkdir(exist_ok=True)

    # 1) Renderiza GIF + WebP y completa metadatos de cada nuevo ejercicio.
    for ex in NUEVOS:
        ex['archivo_svg'] = f"svg/{ex['id'].lower()}-{slug(ex['nombre'])}.svg"
        archivo_gif, fases = engine.save_gif(ex)
        ex['archivo_gif'] = archivo_gif
        ex['secuencia_animacion'] = fases
        stem = Path(archivo_gif).stem
        to_webp(ROOT / archivo_gif, ROOT / 'webp' / f'{stem}.webp')
        ex['gif'] = f'webp/{stem}.webp'
        print(f"✔ {ex['id']} · {ex['nombre']}")

    ids = {ex['id'] for ex in NUEVOS}

    # 2) ejercicios.json (evita duplicar si se reejecuta).
    ejson = ROOT / 'ejercicios.json'
    data = json.loads(ejson.read_text(encoding='utf-8'))
    fields_json = ['id', 'nombre', 'jugadores', 'objetivo', 'nivel', 'duracion_min', 'material', 'instrucciones', 'diagram', 'archivo_svg', 'archivo_gif', 'secuencia_animacion']
    data['ejercicios'] = [e for e in data['ejercicios'] if e['id'] not in ids]
    data['ejercicios'] += [{k: ex[k] for k in fields_json} for ex in NUEVOS]
    data['total'] = len(data['ejercicios'])
    ejson.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    # 3) ejercicios.csv
    with (ROOT / 'ejercicios.csv').open('w', encoding='utf-8-sig', newline='') as f:
        cols = ['id', 'nombre', 'jugadores', 'objetivo', 'nivel', 'duracion_min', 'material', 'instrucciones', 'archivo_svg', 'archivo_gif']
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for e in data['ejercicios']:
            w.writerow({k: e.get(k, '') for k in cols})

    # 4) index.html: añade las tarjetas nuevas (sin duplicar).
    index = ROOT / 'index.html'
    html = index.read_text(encoding='utf-8')
    cards = ''
    for ex in NUEVOS:
        if f'{ex["id"]} ·' in html:
            continue
        jug = f"{ex['jugadores']} jugador{'es' if ex['jugadores'] == 2 else ''}"
        seq = ' → '.join(htmlmod.escape(s) for s in ex['secuencia_animacion'])
        cards += (f'<article class="card" data-p="{ex["jugadores"]}" data-o="{ex["objetivo"]}" data-n="{ex["nivel"]}">'
                  f'<img loading="lazy" src="{ex["gif"]}" alt="{htmlmod.escape(ex["nombre"], quote=True)}">'
                  f'<div><b>{ex["id"]} · {htmlmod.escape(ex["nombre"])}</b>'
                  f'<span>{jug} · {ex["nivel"]} · {ex["duracion_min"]} min</span>'
                  f'<p>{htmlmod.escape(ex["instrucciones"])}</p>'
                  f'<p><b>Secuencia:</b> {seq}</p></div></article>')
    if cards:
        html = html.replace('</main>', cards + '</main>', 1)
        index.write_text(html, encoding='utf-8')

    # 5) data.js: añade los ejercicios (con ruta WebP) conservando el resto.
    djs = ROOT / 'data.js'
    prefix = 'window.TRAINING_DATA='
    raw = djs.read_text(encoding='utf-8')
    payload = json.loads(raw[len(prefix):].rstrip().rstrip(';'))
    fields_data = fields_json + ['gif']
    for ex in NUEVOS:
        payload['exercises'][ex['id']] = {k: ex[k] for k in fields_data}
    djs.write_text(prefix + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';', encoding='utf-8')

    print(f"Ejercicios añadidos: {len(NUEVOS)} · total catálogo: {data['total']}")


if __name__ == '__main__':
    main()
