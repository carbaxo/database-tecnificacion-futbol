from pathlib import Path
import os
import json, csv, html

ROOT=Path(os.environ.get('OUTPUT_DIR','tecnificacion_futbol_svg'))
EX={e['id']:e for e in json.loads((ROOT/'ejercicios.json').read_text(encoding='utf-8'))['ejercicios']}

templates=[
 ('SOLO-INICIACION','Individual · iniciación',1,'iniciación',[
  ('Dominio y conducción',['IND-13','IND-02','IND-01','IND-07']),
  ('Pase y primer control',['IND-04','IND-05','IND-17','IND-10']),
  ('Giros y finalización',['IND-03','IND-09','IND-08','IND-20'])]),
 ('SOLO-INTERMEDIO','Individual · intermedio',1,'intermedio',[
  ('Cambios de dirección',['IND-06','IND-11','IND-14','IND-18']),
  ('Precisión y reacción',['IND-04','IND-05','IND-15','IND-17']),
  ('Circuito y tiro',['IND-08','IND-09','IND-12','IND-20'])]),
 ('SOLO-AVANZADO','Individual · avanzado',1,'avanzado',[
  ('Velocidad técnica',['IND-10','IND-17','IND-19','IND-16']),
  ('Regate bajo fatiga',['IND-12','IND-15','IND-18','IND-06']),
  ('Finalización exigente',['IND-20','IND-08','IND-11','IND-03'])]),
 ('PAREJA-INICIACION','Pareja · iniciación',2,'iniciación',[
  ('Pase y apoyo',['PAR-02','PAR-06','PAR-01','PAR-14']),
  ('Control orientado',['PAR-04','PAR-10','PAR-15','PAR-20']),
  ('Movimiento tras pase',['PAR-03','PAR-08','PAR-11','PAR-13'])]),
 ('PAREJA-INTERMEDIO','Pareja · intermedio',2,'intermedio',[
  ('Pared y desmarque',['PAR-13','PAR-03','PAR-08','PAR-18']),
  ('Control y precisión',['PAR-04','PAR-10','PAR-15','PAR-20']),
  ('Asistencia y tiro',['PAR-09','PAR-12','PAR-19','PAR-06'])]),
 ('PAREJA-AVANZADO','Pareja · avanzado',2,'avanzado',[
  ('Protección y presión',['PAR-07','PAR-16','PAR-17','PAR-20']),
  ('Velocidad de combinación',['PAR-03','PAR-13','PAR-14','PAR-18']),
  ('Finalización combinada',['PAR-09','PAR-12','PAR-19','PAR-11'])]),
]

def session(day,title,ids,duration):
    if duration==30:
        blocks=[
          dict(tipo='calentamiento',minutos=5,descripcion='Movilidad, activación y contactos libres con balón.'),
          *[dict(tipo='ejercicio',ejercicio_id=i,minutos=9,descripcion=EX[i]['nombre']) for i in ids[:2]],
          dict(tipo='reto',minutos=4,descripcion='Repite el ejercicio más difícil intentando superar tu mejor marca.'),
          dict(tipo='vuelta_calma',minutos=3,descripcion='Conducción suave y movilidad.')]
    else:
        blocks=[
          dict(tipo='calentamiento',minutos=8,descripcion='Movilidad, activación, conducción libre y ambos perfiles.'),
          *[dict(tipo='ejercicio',ejercicio_id=i,minutos=10,descripcion=EX[i]['nombre']) for i in ids],
          dict(tipo='reto',minutos=7,descripcion='Ronda cronometrada: máxima precisión manteniendo buena técnica.'),
          dict(tipo='vuelta_calma',minutos=5,descripcion='Toques suaves, respiración y movilidad.')]
    assert sum(b['minutos'] for b in blocks)==duration
    return dict(dia=day,titulo=title,duracion_min=duration,bloques=blocks)

plans=[]
for base,title,players,level,days in templates:
    for duration in (30,60):
        plans.append(dict(
          id=f'{base}-{duration}',nombre=f'{title} · {duration} min',jugadores=players,nivel=level,
          dias_semana=3,duracion_sesion_min=duration,duracion_programa_semanas=4,
          progresion_semanal=[
            'Semana 1: ejecución limpia y ritmo moderado.',
            'Semana 2: aumenta la velocidad sin perder precisión.',
            'Semana 3: prioriza el pie menos hábil y reduce toques.',
            'Semana 4: registra tiempos, aciertos y mejor marca.'
          ],
          sesiones=[session(i+1,t,ids,duration) for i,(t,ids) in enumerate(days)]))

payload=dict(version='1.0',idioma='es',frecuencia='3 días por semana',duraciones_disponibles_min=[30,60],total_planes=len(plans),planes=plans)
(ROOT/'planes_entrenamiento.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')

with (ROOT/'planes_entrenamiento.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['plan_id','plan','jugadores','nivel','duracion_sesion_min','dia','objetivo_dia','orden','tipo','ejercicio_id','ejercicio','minutos','descripcion']
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for p in plans:
      for s in p['sesiones']:
       for order,b in enumerate(s['bloques'],1):
        eid=b.get('ejercicio_id','')
        w.writerow(dict(plan_id=p['id'],plan=p['nombre'],jugadores=p['jugadores'],nivel=p['nivel'],duracion_sesion_min=p['duracion_sesion_min'],dia=s['dia'],objetivo_dia=s['titulo'],orden=order,tipo=b['tipo'],ejercicio_id=eid,ejercicio=EX[eid]['nombre'] if eid else '',minutos=b['minutos'],descripcion=b['descripcion']))

md=['# Planes de tecnificación','',f'{len(plans)} planes de cuatro semanas, con 3 sesiones por semana. Cada modalidad tiene versión de 30 y 60 minutos.','']
for p in plans:
    md += [f"## {p['nombre']}",'',f"**Jugadores:** {p['jugadores']} · **Nivel:** {p['nivel']} · **Duración:** {p['duracion_sesion_min']} min",'']
    for s in p['sesiones']:
        md += [f"### Día {s['dia']} · {s['titulo']}",'']
        for b in s['bloques']:
            ref=f" — **{b['ejercicio_id']}**" if b.get('ejercicio_id') else ''
            md.append(f"- {b['minutos']} min{ref}: {b['descripcion']}")
        md.append('')
    md += ['**Progresión:** '+ ' '.join(p['progresion_semanal']),'']
(ROOT/'PLANES.md').write_text('\n'.join(md),encoding='utf-8')

cards=[]
for p in plans:
    sessions=[]
    for s in p['sesiones']:
        rows=''.join(f"<li><b>{b['minutos']} min</b> · {html.escape((b.get('ejercicio_id','')+' '+b['descripcion']).strip())}</li>" for b in s['bloques'])
        sessions.append(f"<section><h3>Día {s['dia']} · {html.escape(s['titulo'])}</h3><ul>{rows}</ul></section>")
    cards.append(f"<article class='plan' data-p='{p['jugadores']}' data-d='{p['duracion_sesion_min']}' data-n='{p['nivel']}'><div class='tag'>{p['jugadores']} jugador{'es' if p['jugadores']>1 else ''} · {p['nivel']} · {p['duracion_sesion_min']} min</div><h2>{html.escape(p['nombre'])}</h2>{''.join(sessions)}</article>")

(ROOT/'planes.html').write_text(f"""<!doctype html><html lang='es'><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Planes de tecnificación</title><style>*{{box-sizing:border-box}}body{{margin:0;font:15px system-ui;background:#eef3f6;color:#102a43}}header{{padding:32px 5vw;background:linear-gradient(135deg,#102a43,#145da0);color:white}}header h1{{margin:0 0 8px}}.filters{{position:sticky;top:0;padding:14px 5vw;background:#fffe;display:flex;gap:10px;box-shadow:0 2px 12px #0002}}select{{padding:10px;border:1px solid #ccd6df;border-radius:8px}}main{{padding:24px 5vw;display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px}}.plan{{background:white;border-radius:16px;padding:20px;box-shadow:0 6px 22px #102a4315}}.tag{{display:inline-block;background:#dceeff;color:#145da0;border-radius:999px;padding:6px 10px;font-size:12px;font-weight:700}}h2{{font-size:21px}}h3{{font-size:15px;margin-bottom:6px;border-top:1px solid #e4ebf1;padding-top:12px}}ul{{margin:0;padding-left:20px;line-height:1.55}}.hide{{display:none}}</style><header><h1>Planes de tecnificación</h1><p>3 días por semana · sesiones de 30 o 60 minutos · progresión de 4 semanas</p></header><div class='filters'><select id='p'><option value=''>Jugadores: todos</option><option value='1'>Individual</option><option value='2'>Pareja</option></select><select id='d'><option value=''>Duración: todas</option><option value='30'>30 minutos</option><option value='60'>60 minutos</option></select><select id='n'><option value=''>Nivel: todos</option><option>iniciación</option><option>intermedio</option><option>avanzado</option></select></div><main>{''.join(cards)}</main><script>const q=s=>document.querySelector(s),f=()=>document.querySelectorAll('.plan').forEach(c=>c.classList.toggle('hide',(q('#p').value&&c.dataset.p!=q('#p').value)||(q('#d').value&&c.dataset.d!=q('#d').value)||(q('#n').value&&c.dataset.n!=q('#n').value)));document.querySelectorAll('select').forEach(x=>x.onchange=f)</script></html>""",encoding='utf-8')
print(f'Planes creados: {len(plans)}')
