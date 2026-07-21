# Biblioteca de tecnificación de fútbol

40 ejercicios: 20 individuales y 20 por parejas.

## Contenido

- `index.html`: catálogo visual animado con filtros.
- `planes.html`: planes filtrables de 3 días por semana.
- `ejercicios.json` y `ejercicios.csv`: base de datos de ejercicios.
- `planes_entrenamiento.json`, `planes_entrenamiento.csv` y `PLANES.md`: base de datos de planes.
- `svg/`: un diagrama vectorial editable por ejercicio.
- `gif/`: una demostración animada por ejercicio.

## Leyenda

- Línea blanca continua: desplazamiento o conducción.
- Línea amarilla discontinua: pase o recorrido del balón.
- Punto verde: inicio. Bandera: final.
- A/B: jugadores.

Los SVG son editables en navegadores, Inkscape, Illustrator, Figma y Canva. Cada ficha incluye objetivo, nivel, duración, material, instrucciones y secuencia animada.

## Planes disponibles

Se incluyen 12 planes de cuatro semanas: individual o por parejas, niveles iniciación, intermedio y avanzado, y sesiones de 30 o 60 minutos. Todos se organizan en tres días por semana.

## App instalable (PWA)

El sitio funciona como aplicación instalable en Android (y escritorio): incluye `manifest.webmanifest`, iconos adaptativos y un service worker (`sw.js`) que guarda en caché los ejercicios ya vistos para poder entrenar sin conexión. Durante el modo entrenamiento la pantalla se mantiene encendida, el cronómetro sigue la hora real aunque la app pase a segundo plano, el móvil vibra al terminar cada bloque y el botón atrás cierra las fichas y el entrenamiento en lugar de salir de la app.

Para regenerar los iconos: `OUTPUT_DIR=. python3 scripts/build_icons.py` (requiere Pillow). Al publicar cambios, incrementa `VERSION` en `sw.js` para invalidar la caché.

## Regenerar la colección

Requiere Node.js y Python con Pillow instalado.

```bash
OUTPUT_DIR=. node scripts/build_catalog.mjs
OUTPUT_DIR=. python3 scripts/build_gifs.py
OUTPUT_DIR=. python3 scripts/build_plans.py
```

Las animaciones usan una línea temporal específica para cada ejercicio. Los pases, controles, desmarques y tiros se sincronizan con la posición del balón.
