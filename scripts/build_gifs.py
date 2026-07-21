from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont
import json, math, sys, html as htmlmod
import csv

ROOT = Path(os.environ.get('OUTPUT_DIR','tecnificacion_futbol_svg'))
GIF = ROOT / 'gif'
GIF.mkdir(exist_ok=True)
W, H = 640, 430
FIELD = (30, 62, 610, 345)
FRAMES = 44

try:
    FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    BOLD = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    SMALL = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
except OSError:
    FONT = BOLD = SMALL = ImageFont.load_default()

# Coordenadas normalizadas dentro del campo. Cada ruta se repite en bucle.
C = {
'IND-01':dict(a=[(.08,.70),(.23,.66),(.35,.35),(.48,.66),(.61,.35),(.74,.66),(.90,.35)],cones=[(.22,.62),(.35,.36),(.48,.62),(.61,.36),(.74,.62),(.87,.36)]),
'IND-02':dict(a=[(.20,.52),(.38,.22),(.62,.22),(.72,.48),(.52,.65),(.34,.48),(.43,.78),(.68,.78),(.78,.52),(.52,.36),(.30,.52),(.20,.52)],cones=[(.50,.32),(.50,.70)]),
'IND-03':dict(a=[(.18,.78),(.18,.22),(.80,.22),(.80,.78),(.18,.78)],cones=[(.18,.22),(.80,.22),(.80,.78),(.18,.78)]),
'IND-04':dict(a=[(.10,.65),(.28,.55),(.48,.40),(.70,.55),(.88,.50),(.70,.55),(.48,.40),(.28,.55)],cones=[(.28,.45),(.28,.64),(.48,.30),(.48,.49),(.68,.45),(.68,.64)],wall=True,ball=[(.12,.66),(.88,.50),(.12,.66)]),
'IND-05':dict(a=[(.48,.56),(.28,.28),(.48,.56),(.28,.78)],cones=[(.25,.25),(.25,.80),(.70,.55)],wall=True,ball=[(.50,.57),(.88,.51),(.50,.57)]),
'IND-06':dict(a=[(.10,.55),(.50,.15),(.90,.52),(.50,.86),(.10,.55)],cones=[(.50,.15),(.90,.52),(.50,.86),(.10,.55)]),
'IND-07':dict(a=[(.10,.56),(.22,.46),(.30,.64),(.38,.46),(.46,.64),(.54,.46),(.62,.64),(.70,.46),(.78,.64),(.90,.55)],ladder=True),
'IND-08':dict(a=[(.08,.78),(.25,.72),(.36,.46),(.48,.70),(.60,.42),(.76,.38)],cones=[(.24,.70),(.36,.45),(.48,.70),(.60,.42)],goal=True),
'IND-09':dict(a=[(.15,.82),(.50,.52),(.25,.18),(.50,.52),(.78,.18),(.50,.52),(.15,.82)],cones=[(.15,.82),(.50,.52),(.25,.18),(.78,.18)]),
'IND-10':dict(a=[(.48,.58),(.27,.24),(.48,.58),(.72,.78),(.48,.58),(.27,.78),(.48,.58),(.72,.24)],cones=[(.25,.22),(.25,.80),(.72,.22),(.72,.80)],colors=True,wall=True,ball=[(.50,.58),(.88,.50),(.50,.58)]),
'IND-11':dict(a=[(.50,.55),(.56,.48),(.47,.43),(.42,.54),(.50,.62),(.78,.82)],cones=[(.50,.55),(.18,.20),(.80,.82)]),
'IND-12':dict(a=[(.06,.80),(.20,.75),(.30,.50),(.40,.72),(.52,.46),(.66,.65),(.78,.36)],cones=[(.20,.74),(.30,.49),(.40,.72),(.52,.45)],wall=True,goal=True),
'IND-13':dict(a=[(.22,.82),(.50,.22),(.78,.82),(.50,.55),(.22,.82)],cones=[(.50,.20),(.22,.84),(.78,.84)]),
'IND-14':dict(a=[(.16,.82),(.16,.20),(.42,.20),(.68,.20),(.68,.65)],cones=[(.16,.84),(.16,.20),(.42,.20),(.68,.20),(.68,.65)]),
'IND-15':dict(a=[(.12,.82),(.42,.66),(.72,.24),(.78,.78),(.24,.24),(.12,.82)],cones=[(.22,.18),(.22,.35),(.42,.58),(.42,.75),(.72,.16),(.72,.33),(.78,.70),(.78,.87)],colors=True),
'IND-16':dict(a=[(.10,.76),(.24,.70),(.36,.40),(.49,.70),(.62,.40),(.75,.70),(.86,.30)],cones=[(.24,.68),(.36,.40),(.49,.68),(.62,.40),(.75,.68)],wall=True,ball=[(.11,.76),(.24,.70),(.36,.40),(.49,.70),(.62,.40),(.75,.70),(.90,.50)]),
'IND-17':dict(a=[(.16,.78),(.32,.78),(.48,.78),(.64,.78),(.80,.78)],cones=[(.16,.82),(.32,.82),(.48,.82),(.64,.82),(.80,.82)],wall_long=True,ball=[(.16,.74),(.24,.20),(.32,.74),(.40,.20),(.48,.74),(.56,.20),(.64,.74),(.72,.20),(.80,.74)]),
'IND-18':dict(a=[(.10,.78),(.24,.72),(.34,.48),(.48,.70),(.60,.44),(.74,.68),(.88,.35)],cones=[(.24,.70),(.36,.48),(.48,.70),(.62,.44),(.76,.68)]),
'IND-19':dict(a=[(.50,.52),(.18,.18),(.50,.52),(.82,.18),(.50,.52),(.82,.84),(.50,.52),(.18,.84),(.50,.52)],cones=[(.50,.52),(.18,.18),(.82,.18),(.82,.84),(.18,.84)]),
'IND-20':dict(a=[(.12,.82),(.34,.62),(.50,.38),(.48,.18),(.88,.82),(.66,.62),(.50,.38),(.52,.18)],cones=[(.22,.76),(.36,.58),(.50,.36),(.64,.58),(.78,.76)],goal=True,ball=[(.14,.82),(.34,.62),(.50,.38),(.48,.14),(.88,.82),(.66,.62),(.50,.38),(.52,.14)]),
'PAR-01':dict(a=[(.20,.80),(.80,.80),(.50,.18),(.20,.80)],b=[(.80,.80),(.50,.18),(.20,.80),(.80,.80)],cones=[(.20,.82),(.80,.82),(.50,.18)],ball=[(.22,.78),(.78,.78),(.50,.20),(.22,.78)]),
'PAR-02':dict(a=[(.20,.55),(.27,.55),(.20,.55)],b=[(.80,.55),(.73,.55),(.80,.55)],cones=[(.14,.30),(.14,.80),(.86,.30),(.86,.80)],ball=[(.23,.55),(.77,.55),(.23,.55)]),
'PAR-03':dict(a=[(.15,.75),(.35,.35),(.55,.28),(.72,.20)],b=[(.60,.55),(.60,.55)],cones=[(.32,.62),(.82,.18),(.82,.82)],ball=[(.17,.73),(.58,.54),(.48,.34),(.68,.22)]),
'PAR-04':dict(a=[(.72,.55),(.58,.76),(.72,.55)],b=[(.18,.55),(.18,.55)],cones=[(.42,.35),(.42,.52),(.57,.58),(.57,.76)],ball=[(.20,.55),(.70,.55),(.58,.74),(.20,.55)]),
'PAR-05':dict(a=[(.22,.62),(.34,.32),(.18,.28),(.28,.72),(.22,.62)],b=[(.68,.62),(.80,.32),(.64,.28),(.74,.72),(.68,.62)],cones=[(.10,.18),(.42,.18),(.42,.84),(.10,.84),(.56,.18),(.90,.18),(.90,.84),(.56,.84)],two_balls=True),
'PAR-06':dict(a=[(.12,.55),(.20,.55),(.12,.55)],b=[(.88,.55),(.80,.55),(.88,.55)],cones=[(.32,.30),(.32,.47),(.50,.55),(.50,.72),(.68,.30),(.68,.47),(.68,.68),(.68,.85)],ball=[(.15,.55),(.35,.38),(.85,.55),(.68,.76),(.15,.55)]),
'PAR-07':dict(a=[(.42,.62),(.32,.42),(.48,.27),(.66,.46),(.58,.70),(.42,.62)],b=[(.60,.54),(.52,.42),(.43,.36),(.54,.55),(.60,.54)],cones=[(.20,.18),(.80,.18),(.80,.85),(.20,.85)]),
'PAR-08':dict(a=[(.16,.82),(.38,.52),(.68,.18),(.82,.14)],b=[(.50,.54),(.50,.54)],cones=[(.16,.82),(.50,.55),(.82,.15),(.82,.84)],ball=[(.18,.80),(.50,.54),(.68,.22),(.80,.16)]),
'PAR-09':dict(a=[(.18,.80),(.42,.42),(.48,.28)],b=[(.64,.80),(.80,.58),(.60,.40)],cones=[(.16,.82),(.62,.82),(.82,.58),(.48,.30)],ball=[(.66,.80),(.80,.58),(.58,.40),(.50,.25)],goal=True),
'PAR-10':dict(a=[(.58,.56),(.78,.28),(.58,.56),(.78,.82)],b=[(.22,.56),(.22,.56)],cones=[(.78,.20),(.78,.38),(.78,.68),(.78,.86)],ball=[(.24,.56),(.56,.56),(.76,.28),(.56,.56),(.76,.82)]),
'PAR-11':dict(a=[(.16,.78),(.85,.78)],b=[(.16,.25),(.85,.25)],cones=[(.10,.88),(.90,.88),(.10,.15),(.90,.15),(.50,.88),(.50,.15)],ball=[(.18,.76),(.36,.28),(.54,.76),(.72,.28),(.86,.76)]),
'PAR-12':dict(a=[(.12,.78),(.36,.50),(.52,.34),(.74,.24)],b=[(.52,.55),(.52,.55)],cones=[(.12,.82),(.35,.55),(.55,.58),(.76,.35)],ball=[(.14,.76),(.50,.54),(.42,.36),(.72,.24)],goal=True),
'PAR-13':dict(a=[(.12,.80),(.38,.55),(.48,.28),(.72,.20)],b=[(.48,.58),(.58,.45),(.66,.26)],cones=[(.12,.84),(.38,.60),(.72,.18),(.78,.78),(.24,.18)],ball=[(.14,.78),(.47,.57),(.66,.25),(.72,.20)]),
'PAR-14':dict(a=[(.50,.54),(.50,.54)],b=[(.50,.18),(.84,.52),(.50,.86),(.16,.52),(.50,.18)],cones=[(.50,.16),(.84,.52),(.50,.88),(.16,.52),(.50,.54)],ball=[(.50,.52),(.50,.20),(.50,.52),(.82,.52),(.50,.52),(.50,.84),(.50,.52),(.18,.52),(.50,.52)]),
'PAR-15':dict(a=[(.70,.55),(.56,.72),(.70,.55)],b=[(.18,.55),(.18,.55)],cones=[(.12,.28),(.12,.82),(.82,.28),(.82,.82)],ball=[(.20,.52),(.42,.20),(.68,.52),(.56,.70),(.20,.58)],aerial=True),
'PAR-16':dict(a=[(.48,.56),(.42,.42),(.34,.58),(.22,.78)],b=[(.58,.54),(.52,.46),(.44,.56),(.34,.70)],cones=[(.16,.18),(.84,.18),(.84,.86),(.16,.86)]),
'PAR-17':dict(a=[(.12,.82),(.28,.68),(.48,.48),(.68,.30),(.86,.18)],b=[(.88,.82),(.72,.68),(.52,.48),(.32,.30),(.14,.18)],cones=[(.26,.20),(.26,.37),(.48,.42),(.48,.59),(.70,.20),(.70,.37),(.70,.67),(.70,.84)],ball=[(.14,.80),(.26,.28),(.86,.80),(.70,.76),(.14,.80)]),
'PAR-18':dict(a=[(.16,.80),(.16,.80)],b=[(.42,.78),(.52,.50),(.70,.28),(.84,.18)],cones=[(.34,.62),(.34,.80),(.58,.35),(.58,.53),(.84,.14),(.84,.84)],ball=[(.18,.78),(.38,.66),(.56,.44),(.80,.20)]),
'PAR-19':dict(a=[(.12,.80),(.40,.52),(.58,.32),(.76,.18)],b=[(.50,.56),(.40,.72),(.30,.82)],cones=[(.12,.84),(.38,.58),(.54,.58),(.76,.32)],ball=[(.14,.78),(.48,.55),(.42,.40),(.74,.18)],goal=True),
'PAR-20':dict(a=[(.18,.55),(.32,.28),(.18,.55),(.32,.82),(.18,.55)],b=[(.82,.55),(.68,.28),(.82,.55),(.68,.82),(.82,.55)],cones=[(.32,.18),(.32,.38),(.32,.72),(.32,.90),(.68,.18),(.68,.38),(.68,.72),(.68,.90)],ball=[(.20,.55),(.80,.55),(.68,.28),(.80,.55),(.20,.55),(.32,.82),(.20,.55)]),
}

def K(points,times=None):
    if times is None: times=[i/(len(points)-1) for i in range(len(points))]
    return [(t,p[0],p[1]) for t,p in zip(times,points)]

# Línea temporal semántica. Las posiciones repetidas representan esperas reales:
# control, apoyo, devolución o preparación del tiro.
M={}
for n in range(1,21):
    key=f'IND-{n:02d}'; M[key]=dict(a=K(C[key]['a']),ball='follow_a',fases=['Conducción técnica','Cambio o gesto','Salida controlada'])

M['IND-04']=dict(
 a=K([(.10,.65),(.28,.55),(.28,.55),(.48,.40),(.48,.40),(.70,.55),(.70,.55)], [0,.12,.31,.42,.61,.72,1]),
 ball=K([(.12,.66),(.28,.55),(.88,.50),(.28,.55),(.48,.40),(.88,.50),(.48,.40),(.70,.55),(.88,.50),(.70,.55)],[0,.12,.21,.31,.42,.51,.61,.72,.81,.92]),
 fases=['Conduce a la puerta','Pase a la pared','Control hacia la siguiente'])
M['IND-05']=dict(
 a=K([(.48,.56),(.48,.56),(.48,.56),(.28,.28),(.48,.56),(.28,.78)],[0,.18,.38,.58,.76,1]),
 ball=K([(.50,.57),(.88,.51),(.50,.57),(.28,.28),(.50,.57),(.28,.78)],[0,.18,.38,.58,.76,1]),
 fases=['Pase a la pared','Perfil corporal','Control orientado 180°'])
M['IND-08']=dict(
 a=K([(.08,.78),(.25,.72),(.36,.46),(.48,.70),(.60,.42),(.64,.39)],[0,.18,.36,.54,.72,1]),
 ball=K([(.08,.78),(.25,.72),(.36,.46),(.48,.70),(.60,.42),(.82,.10)],[0,.18,.36,.54,.72,1]),
 fases=['Slalom','Recorte','Tiro al palo largo'])
M['IND-10']=dict(
 a=K([(.48,.58),(.48,.58),(.48,.58),(.72,.78),(.48,.58),(.27,.24)],[0,.18,.36,.58,.76,1]),
 ball=K([(.50,.58),(.88,.50),(.50,.58),(.72,.78),(.50,.58),(.27,.24)],[0,.18,.36,.58,.76,1]),
 fases=['Pase a la pared','Escanea el color','Primer toque hacia la puerta'])
M['IND-12']=dict(
 a=K([(.06,.80),(.20,.75),(.30,.50),(.40,.72),(.52,.46),(.62,.60),(.68,.56)],[0,.13,.27,.40,.53,.72,1]),
 ball=K([(.06,.80),(.20,.75),(.30,.50),(.40,.72),(.52,.46),(.88,.52),(.62,.60),(.82,.10)],[0,.13,.27,.40,.53,.63,.72,1]),
 fases=['Slalom','Pared y control','Finalización'])
M['IND-16']=dict(
 a=K([(.10,.76),(.24,.70),(.36,.40),(.49,.70),(.62,.40),(.75,.70),(.79,.64)],[0,.15,.30,.45,.60,.75,1]),
 ball=K([(.10,.76),(.24,.70),(.36,.40),(.49,.70),(.62,.40),(.75,.70),(.90,.50)],[0,.15,.30,.45,.60,.75,1]),
 fases=['Solo pie débil','Giro con planta','Pase final'])
M['IND-17']=dict(
 a=K([(.16,.78),(.16,.78),(.32,.78),(.32,.78),(.48,.78),(.48,.78),(.64,.78),(.64,.78),(.80,.78)],[0,.10,.23,.33,.46,.56,.69,.79,1]),
 ball=K([(.16,.74),(.24,.20),(.16,.74),(.32,.74),(.40,.20),(.32,.74),(.48,.74),(.56,.20),(.48,.74),(.64,.74),(.72,.20),(.64,.74),(.80,.74)],[0,.07,.14,.23,.30,.37,.46,.53,.60,.69,.76,.83,1]),
 fases=['Pase de primeras','Desplazamiento lateral','Repite sin detener el balón'])
M['IND-20']=dict(
 a=K([(.12,.82),(.34,.62),(.50,.38),(.50,.34),(.88,.82),(.66,.62),(.50,.38),(.50,.34)],[0,.16,.32,.46,.54,.70,.86,1]),
 ball=K([(.12,.82),(.34,.62),(.50,.38),(.80,.10),(.88,.82),(.66,.62),(.50,.38),(.84,.10)],[0,.16,.32,.46,.54,.70,.86,1]),
 fases=['Entrada izquierda y tiro','Cambio de lado','Entrada derecha y tiro'])

M.update({
'PAR-01':dict(a=K([(.20,.80),(.20,.80),(.50,.18),(.50,.18),(.80,.80)],[0,.18,.42,.68,1]),b=K([(.80,.80),(.80,.80),(.80,.80),(.20,.80),(.20,.80)],[0,.18,.42,.68,1]),ball=K([(.20,.80),(.80,.80),(.80,.80),(.50,.18),(.50,.18)],[0,.18,.42,.68,1]),fases=['A pasa a B','A ocupa el vértice libre','B pasa a A']),
'PAR-02':dict(a=K([(.20,.55),(.20,.55)]),b=K([(.80,.55),(.80,.55)]),ball=K([(.20,.55),(.80,.55),(.80,.55),(.20,.55)],[0,.30,.55,1]),fases=['Control orientado','Pase con el otro pie','Cambio de receptor']),
'PAR-03':dict(a=K([(.15,.75),(.15,.75),(.35,.35),(.55,.28),(.72,.20)],[0,.18,.42,.70,1]),b=K([(.60,.55),(.60,.55)]),ball=K([(.15,.75),(.60,.55),(.48,.34),(.68,.22)],[0,.18,.42,1]),fases=['A pasa a B','A acelera por fuera','B devuelve al espacio']),
'PAR-04':dict(a=K([(.72,.55),(.72,.55),(.58,.76),(.58,.76)],[0,.28,.58,1]),b=K([(.18,.55),(.18,.55)]),ball=K([(.18,.55),(.72,.55),(.58,.76),(.18,.55)],[0,.28,.58,1]),fases=['B pasa a A','A cruza la puerta con el control','A devuelve a B']),
'PAR-05':dict(a=K(C['PAR-05']['a']),b=K(C['PAR-05']['b']),ball='two_follow',fases=['A lidera','B copia el gesto','Cambio de dirección sincronizado']),
'PAR-06':dict(a=K([(.12,.55),(.20,.40),(.20,.40),(.12,.70)],[0,.25,.60,1]),b=K([(.88,.55),(.80,.70),(.80,.70),(.88,.35)],[0,.25,.60,1]),ball=K([(.12,.55),(.35,.38),(.80,.70),(.68,.76),(.12,.70)],[0,.25,.48,.72,1]),fases=['A elige una puerta','Pase a B','B cambia de puerta y devuelve']),
'PAR-07':dict(a=K(C['PAR-07']['a']),b=K(C['PAR-07']['b']),ball='follow_a',fases=['A protege y cambia de dirección','B presiona progresivamente','Cambio de rol al robo']),
'PAR-08':dict(a=K([(.16,.82),(.16,.82),(.38,.52),(.68,.18),(.82,.14)],[0,.20,.44,.72,1]),b=K([(.50,.54),(.50,.54)]),ball=K([(.16,.82),(.50,.54),(.50,.54),(.80,.16)],[0,.20,.50,1]),fases=['A pasa a B','A se desmarca en diagonal','B devuelve al espacio']),
'PAR-09':dict(a=K([(.18,.80),(.18,.80),(.42,.42),(.48,.28)],[0,.35,.70,1]),b=K([(.64,.80),(.80,.58),(.60,.40),(.60,.40)],[0,.35,.60,1]),ball=K([(.64,.80),(.80,.58),(.60,.40),(.42,.42),(.82,.10)],[0,.35,.60,.72,1]),fases=['B conduce','Asistencia atrás','A llega y finaliza']),
'PAR-10':dict(a=K([(.58,.56),(.58,.56),(.78,.28),(.78,.28)],[0,.30,.65,1]),b=K([(.22,.56),(.22,.56)]),ball=K([(.22,.56),(.58,.56),(.78,.28),(.78,.28)],[0,.30,.65,1]),fases=['B indica puerta y pasa','A orienta el control','A sale por la puerta']),
'PAR-11':dict(a=K([(.16,.78),(.34,.78),(.52,.78),(.70,.78),(.85,.78)]),b=K([(.16,.25),(.34,.25),(.52,.25),(.70,.25),(.85,.25)]),ball=K([(.16,.78),(.34,.25),(.52,.78),(.70,.25),(.85,.78)]),fases=['Avance en paralelo','Pase al espacio','Receptor acompaña la carrera']),
'PAR-12':dict(a=K([(.12,.78),(.12,.78),(.36,.50),(.52,.34),(.58,.30)],[0,.18,.44,.72,1]),b=K([(.52,.55),(.52,.55)]),ball=K([(.12,.78),(.52,.55),(.42,.36),(.52,.34),(.76,.12)],[0,.18,.44,.72,1]),fases=['A juega con B','Pared y desmarque','A controla y finaliza']),
'PAR-13':dict(a=K([(.12,.80),(.12,.80),(.38,.55),(.48,.28),(.72,.20)],[0,.18,.42,.70,1]),b=K([(.48,.58),(.48,.58),(.58,.45),(.66,.26)],[0,.18,.55,1]),ball=K([(.12,.80),(.48,.58),(.48,.58),(.68,.23)],[0,.18,.55,1]),fases=['A pasa a B','A dobla por fuera','B devuelve al espacio']),
'PAR-14':dict(a=K([(.50,.54),(.50,.54)]),b=K([(.50,.18),(.50,.18),(.84,.52),(.84,.52),(.50,.86),(.50,.86),(.16,.52),(.16,.52)],[0,.12,.25,.37,.50,.62,.75,1]),ball=K([(.50,.54),(.50,.18),(.50,.54),(.84,.52),(.50,.54),(.50,.86),(.50,.54),(.16,.52),(.50,.54)],[0,.12,.22,.34,.44,.56,.66,.78,1]),fases=['Pase desde el centro','B cambia de posición','Devolución y siguiente punto']),
'PAR-15':dict(a=K([(.70,.55),(.70,.55),(.56,.72),(.56,.72)],[0,.38,.68,1]),b=K([(.18,.55),(.18,.55)]),ball=K([(.18,.55),(.44,.22),(.70,.55),(.56,.72),(.18,.55)],[0,.20,.38,.68,1]),fases=['B envía balón aéreo','A amortigua y conduce','Devolución por el suelo']),
'PAR-16':dict(a=K(C['PAR-16']['a']),b=K(C['PAR-16']['b']),ball='follow_a',fases=['A protege el balón','B presiona sin robar','A gira y sale por la puerta']),
'PAR-17':dict(a=K([(.12,.82),(.28,.68),(.28,.68),(.48,.48),(.68,.30)],[0,.22,.48,.72,1]),b=K([(.88,.82),(.72,.68),(.72,.68),(.52,.48),(.32,.30)],[0,.22,.48,.72,1]),ball=K([(.12,.82),(.28,.28),(.72,.68),(.70,.76),(.48,.48),(.26,.28),(.32,.30)],[0,.16,.32,.48,.64,.82,1]),fases=['A y B buscan puerta','Pase válido suma punto','Reposición para otra puerta']),
'PAR-18':dict(a=K([(.16,.80),(.16,.80)]),b=K([(.42,.78),(.52,.50),(.70,.28),(.84,.18)]),ball=K([(.16,.80),(.16,.80),(.56,.44),(.82,.20)],[0,.24,.58,1]),fases=['B inicia la ruptura','A espera y temporiza','Pase por delante de B']),
'PAR-19':dict(a=K([(.12,.80),(.12,.80),(.40,.52),(.58,.32),(.68,.24)],[0,.18,.44,.72,1]),b=K([(.50,.56),(.50,.56),(.40,.72),(.30,.82)],[0,.18,.55,1]),ball=K([(.12,.80),(.50,.56),(.42,.40),(.58,.32),(.76,.12)],[0,.18,.44,.72,1]),fases=['A juega pared con B','Carreras cruzadas','Devolución y tiro']),
'PAR-20':dict(a=K([(.18,.55),(.18,.55),(.32,.28),(.18,.55),(.18,.55),(.32,.82),(.18,.55)],[0,.18,.34,.48,.66,.82,1]),b=K([(.82,.55),(.68,.28),(.82,.55),(.82,.55),(.68,.82),(.82,.55)],[0,.18,.34,.66,.82,1]),ball=K([(.18,.55),(.82,.55),(.68,.28),(.82,.55),(.18,.55),(.32,.82),(.18,.55)],[0,.18,.34,.48,.66,.82,1]),fases=['Pase y control hacia puerta alta','Devolución','Control alterno hacia puerta baja']),
})

# Ejercicios avanzados añadidos a la biblioteca.
C.update({
'IND-21':dict(a=[(.10,.78),(.24,.68),(.34,.48),(.48,.68),(.60,.44),(.74,.66),(.90,.40)],cones=[(.24,.66),(.36,.48),(.48,.66),(.62,.44),(.76,.64)]),
'IND-22':dict(a=[(.50,.56),(.43,.47),(.50,.40),(.58,.48),(.51,.58),(.44,.50),(.22,.24)],cones=[(.50,.52),(.22,.22),(.80,.80)]),
'IND-23':dict(a=[(.50,.56),(.50,.56),(.28,.24),(.50,.56),(.74,.80)],cones=[(.26,.22),(.74,.22),(.26,.82),(.74,.82)],colors=True),
'PAR-21':dict(a=[(.24,.60),(.34,.34),(.20,.30),(.30,.70),(.24,.60)],b=[(.66,.60),(.76,.34),(.62,.30),(.72,.70),(.66,.60)],cones=[(.10,.18),(.42,.18),(.42,.84),(.10,.84),(.58,.18),(.90,.18),(.90,.84),(.58,.84)],two_balls=True),
'PAR-22':dict(a=[(.16,.80),(.34,.64),(.46,.58)],b=[(.42,.74),(.58,.46),(.76,.26)],cones=[(.34,.62),(.58,.40),(.84,.16),(.16,.84)],ball=[(.18,.78),(.60,.44),(.46,.58),(.80,.24)]),
'PAR-23':dict(a=[(.20,.55),(.20,.55)],b=[(.62,.55),(.80,.30),(.62,.55),(.80,.80)],cones=[(.80,.20),(.80,.38),(.80,.68),(.80,.86),(.20,.55),(.62,.55)],ball=[(.20,.55),(.62,.55),(.80,.30),(.62,.55),(.80,.80)]),
})
M.update({
'IND-21':dict(a=K(C['IND-21']['a']),ball='follow_a',fases=['Ataca el cono','Finta y recorte','Salida en velocidad']),
'IND-22':dict(a=K([(.50,.56),(.43,.47),(.50,.40),(.58,.48),(.51,.58),(.44,.50),(.22,.24)],[0,.16,.32,.48,.62,.76,1]),ball='follow_a',fases=['Protege girando','Cambia de perfil','Sal en conducción']),
'IND-23':dict(a=K([(.50,.56),(.50,.56),(.28,.24),(.50,.56),(.74,.80)],[0,.28,.56,.78,1]),ball='follow_a',fases=['Conduce al centro','Lee el color','Sal orientado']),
'PAR-21':dict(a=K(C['PAR-21']['a']),b=K(C['PAR-21']['b']),ball='two_follow',fases=['A marca el ritmo','B replica el gesto','Cambio sincronizado']),
'PAR-22':dict(a=K([(.16,.80),(.16,.80),(.34,.64),(.46,.58),(.46,.58)],[0,.24,.5,.74,1]),b=K([(.42,.74),(.55,.50),(.60,.44),(.58,.50),(.60,.44)],[0,.3,.5,.7,1]),ball=K([(.18,.78),(.18,.78),(.60,.44),(.46,.58),(.80,.24)],[0,.24,.5,.74,1]),fases=['B rompe al espacio','Recibe de cara','Descarga y pase final']),
'PAR-23':dict(a=K([(.20,.55),(.20,.55)]),b=K([(.62,.55),(.62,.55),(.80,.30),(.62,.55),(.80,.80)],[0,.3,.55,.75,1]),ball=K([(.20,.55),(.62,.55),(.80,.30),(.62,.55),(.80,.80)],[0,.3,.55,.75,1]),fases=['A pasa','B lee la puerta','Devuelve o gira y sale']),
})

def xy(p):
    x0,y0,x1,y1=FIELD
    return (x0+p[0]*(x1-x0), y0+p[1]*(y1-y0))

def lerp_route(route,t):
    if len(route)==1:return xy(route[0])
    lengths=[]; total=0
    pts=[xy(p) for p in route]
    for p,q in zip(pts,pts[1:]):
        d=math.hypot(q[0]-p[0],q[1]-p[1]); lengths.append(d); total+=d
    target=max(0,min(1,t))*total
    for i,d in enumerate(lengths):
        if target<=d:
            u=target/d if d else 0
            return (pts[i][0]+(pts[i+1][0]-pts[i][0])*u,pts[i][1]+(pts[i+1][1]-pts[i][1])*u)
        target-=d
    return pts[-1]

def route_pose(route,t):
    p=lerp_route(route,t)
    p2=lerp_route(route,min(1,t+.015))
    if abs(p2[0]-p[0])+abs(p2[1]-p[1])<1:
        p0=lerp_route(route,max(0,t-.015)); p2=p
        ang=math.atan2(p2[1]-p0[1],p2[0]-p0[0])
    else: ang=math.atan2(p2[1]-p[1],p2[0]-p[0])
    return p,ang

def key_pose(keys,t):
    if len(keys)==1:return xy((keys[0][1],keys[0][2])),0
    t=max(0,min(1,t))
    for i,(ta,xa,ya) in enumerate(keys[:-1]):
        tb,xb,yb=keys[i+1]
        if t<=tb:
            u=(t-ta)/(tb-ta) if tb>ta else 0
            # Suaviza cada gesto sin desplazar los contactos de pase/control.
            u=u*u*(3-2*u)
            p=xy((xa+(xb-xa)*u,ya+(yb-ya)*u))
            ang=math.atan2(yb-ya,xb-xa) if abs(xb-xa)+abs(yb-ya)>.001 else 0
            return p,ang
    return xy((keys[-1][1],keys[-1][2])),0

def cone(draw,p,color='#ff7a00'):
    x,y=xy(p)
    draw.ellipse((x-13,y+8,x+13,y+14),fill='#0d4229')
    draw.polygon([(x,y-11),(x-8,y+8),(x+8,y+8)],fill=color,outline='#6b3100')
    draw.line((x-5,y+1,x+5,y+1),fill='white',width=2)
    draw.rounded_rectangle((x-12,y+7,x+12,y+12),2,fill=color,outline='#6b3100')

def person(draw,p,label,color,ang=0):
    x,y=p
    ux,uy=math.cos(ang),math.sin(ang); px,py=-uy,ux
    draw.ellipse((x-16,y-9,x+16,y+11),fill='#0b3e27')
    tip=(x+ux*22,y+uy*22); left=(x+px*8-ux*5,y+py*8-uy*5); right=(x-px*8-ux*5,y-py*8-uy*5)
    draw.polygon([tip,left,right],fill='white')
    draw.ellipse((x-14,y-14,x+14,y+14),fill='white')
    draw.ellipse((x-11,y-11,x+11,y+11),fill=color,outline='#0b3159',width=2)
    draw.ellipse((x+ux*8-5,y+uy*8-5,x+ux*8+5,y+uy*8+5),fill='#f2c7a5',outline='white')
    draw.text((x-ux*4,y-uy*4),label,font=SMALL,anchor='mm',fill='white',stroke_width=1,stroke_fill='#0b3159')

def football(draw,p,pulse=0):
    x,y=p; glow=10+int(2*pulse)
    draw.ellipse((x-glow,y-glow,x+glow,y+glow),fill='#ffe66d')
    draw.ellipse((x-7,y-7,x+7,y+7),fill='white',outline='#101820',width=2)
    draw.polygon([(x,y-3),(x+3,y-1),(x+2,y+3),(x-2,y+4),(x-4,y)],fill='#101820')

def dashed(draw,pts,fill,width=3,dash=10,gap=7):
    for p,q in zip(pts,pts[1:]):
        dx,dy=q[0]-p[0],q[1]-p[1]; length=math.hypot(dx,dy)
        if not length: continue
        u=0
        while u<length:
            v=min(length,u+dash)
            draw.line((p[0]+dx*u/length,p[1]+dy*u/length,p[0]+dx*v/length,p[1]+dy*v/length),fill=fill,width=width)
            u+=dash+gap

def arrowhead(draw,route,color):
    if len(route)<2:return
    p,q=xy(route[-2]),xy(route[-1]); a=math.atan2(q[1]-p[1],q[0]-p[0])
    pts=[q,(q[0]-15*math.cos(a-.45),q[1]-15*math.sin(a-.45)),(q[0]-15*math.cos(a+.45),q[1]-15*math.sin(a+.45))]
    draw.polygon(pts,fill=color)

def base(ex,cfg):
    im=Image.new('RGB',(W,H),'#eef3f6'); d=ImageDraw.Draw(im)
    d.text((28,14),f"{ex['id']} · {ex['nombre']}",font=BOLD,fill='#102a43')
    badge=ex['objetivo'].upper(); bw=d.textbbox((0,0),badge,font=SMALL)[2]+24
    d.rounded_rectangle((W-bw-28,15,W-28,39),12,fill='#dceeff')
    d.text((W-bw/2-28,27),badge,font=SMALL,anchor='mm',fill='#145da0')
    x0,y0,x1,y1=FIELD; d.rounded_rectangle(FIELD,10,fill='#168447',outline='#0f5933',width=4)
    for i in range(8):
        xx=x0+i*(x1-x0)/8; d.rectangle((xx,y0,xx+(x1-x0)/16,y1),fill='#197a43')
    d.rectangle((x0+14,y0+14,x1-14,y1-14),outline=(255,255,255),width=2)
    colors=['#ef4444','#3b82f6','#facc15','#22c55e'] if cfg.get('colors') else []
    for i,p in enumerate(cfg.get('cones',[])): cone(d,p,colors[i%4] if colors else '#ff7a00')
    if cfg.get('wall'): d.rounded_rectangle((548,190,597,202),3,fill='#cbd5e1',outline='#475569',width=2)
    if cfg.get('wall_long'):
        d.rounded_rectangle((135,108,505,120),3,fill='#cbd5e1',outline='#475569',width=2)
        for xx in range(150,500,28): d.line((xx,109,xx,119),fill='#64748b',width=1)
    if cfg.get('goal'):
        d.line((460,70,575,70,575,105),fill='white',width=4); d.line((460,70,460,105),fill='white',width=4)
        for xx in range(470,575,18): d.line((xx,70,xx,103),fill='#dbeafe',width=1)
        for yy in range(80,105,10): d.line((460,yy,575,yy),fill='#dbeafe',width=1)
    if cfg.get('ladder'):
        for i in range(7): d.rectangle((150+i*55,175,205+i*55,245),outline='white',width=3)
    # Rutas: blanco = conducción/desplazamiento, amarillo = balón/pase.
    for key,col in [('a','#ffffff'),('b','#b9ddff')]:
        if key in cfg:
            pts=[xy(p) for p in cfg[key]]
            if len(pts)>1:
                d.line(pts,fill='#0b5335',width=7)
                d.line(pts,fill=col,width=3)
                arrowhead(d,cfg[key],col)
    if 'ball' in cfg:
        pts=[xy(p) for p in cfg['ball']]
        dashed(d,pts,'#ffd43b',3)
        arrowhead(d,cfg['ball'],'#ffd43b')
    # Inicio y final del recorrido principal.
    sx,sy=xy(cfg['a'][0]); exx,eyy=xy(cfg['a'][-1])
    d.ellipse((sx-6,sy-6,sx+6,sy+6),fill='#22c55e',outline='white',width=2)
    if math.hypot(exx-sx,eyy-sy)>12:
        d.rectangle((exx-6,eyy-9,exx+6,eyy+5),fill='white',outline='#102a43')
        d.rectangle((exx,eyy-9,exx+6,eyy-2),fill='#102a43')
    d.rounded_rectangle((30,360,610,414),10,fill='white',outline='#d8e0e8')
    text=ex['instrucciones']; text=text if len(text)<88 else text[:85]+'…'
    d.text((45,373),text,font=SMALL,fill='#334e68')
    d.text((45,393),'Blanco: jugador/conducción   ·   Amarillo: pase o recorrido del balón',font=SMALL,fill='#486581')
    return im

def render_frames(ex):
    """Genera los fotogramas del GIF de un ejercicio a partir de C[id] y M[id]."""
    cfg=C[ex['id']]; anim=M[ex['id']]; frames=[]
    for i in range(FRAMES):
        t=i/(FRAMES-1)
        move=min(t/.94,1)
        im=base(ex,cfg); d=ImageDraw.Draw(im)
        pa,aa=key_pose(anim['a'],move)
        pb=None
        if 'b' in anim: pb,ab=key_pose(anim['b'],move)
        ball_spec=anim['ball']
        if ball_spec=='follow_a':
            bp=(pa[0]+18*math.cos(aa),pa[1]+18*math.sin(aa))
        elif ball_spec=='two_follow':
            bp=(pa[0]+18*math.cos(aa),pa[1]+18*math.sin(aa))
        else:
            bp,_=key_pose(ball_spec,move)
        # Estela corta: ayuda a leer la dirección sin saturar la imagen.
        for j,alpha in enumerate((.20,.38,.58),1):
            old=max(0,move-j*.025)
            if ball_spec in ('follow_a','two_follow'):
                op,oa=key_pose(anim['a'],old); tp=(op[0]+18*math.cos(oa),op[1]+18*math.sin(oa))
            else: tp,_=key_pose(ball_spec,old)
            r=2+j; col=(255,211+int(30*alpha),70)
            d.ellipse((tp[0]-r,tp[1]-r,tp[0]+r,tp[1]+r),fill=col)
        person(d,pa,'A' if ex['jugadores']==2 else '1','#1778d4',aa)
        if pb is not None: person(d,pb,'B','#e63946',ab)
        if ball_spec=='two_follow':
            football(d,bp,math.sin(t*math.pi*2))
            bp2=(pb[0]+18*math.cos(ab),pb[1]+18*math.sin(ab)); football(d,bp2,math.sin(t*math.pi*2))
        else:
            football(d,bp,math.sin(t*math.pi*2))
        # Etiqueta contextual y barra temporal.
        idx=min(len(anim['fases'])-1,int(move*len(anim['fases'])))
        phase=anim['fases'][idx].upper()
        passing=any(w in phase for w in ('PASE','DEVOLUCIÓN','PARED','ENVÍA','ASISTENCIA','DESCARGA'))
        color='#e6a800' if passing else ('#d9485f' if 'TIRO' in phase or 'FINALIZA' in phase else '#1778d4')
        d.rounded_rectangle((43,77,43+d.textbbox((0,0),phase,font=SMALL)[2]+22,101),12,fill=color)
        d.text((54,89),phase,font=SMALL,anchor='lm',fill='white')
        d.rounded_rectangle((45,407,595,411),2,fill='#dbe4ec')
        d.rounded_rectangle((45,407,45+550*move,411),2,fill=color)
        frames.append(im.quantize(colors=128,method=Image.Quantize.MEDIANCUT))
    return frames,anim['fases']

def save_gif(ex):
    frames,fases=render_frames(ex)
    name=Path(ex['archivo_svg']).stem+'.gif'
    frames[0].save(GIF/name,save_all=True,append_images=frames[1:],duration=85,loop=0,optimize=True,disposal=2)
    return 'gif/'+name,fases

# Ejecutado directamente: regenera todos los GIF y reescribe la base y el catálogo.
# Importado como módulo (build_extra.py) solo expone C, M y las funciones del motor.
if __name__=='__main__':
    data=json.loads((ROOT/'ejercicios.json').read_text(encoding='utf-8-sig'))
    selected=set(sys.argv[1:])
    generated=0
    for ex in data['ejercicios']:
        if selected and ex['id'] not in selected:
            continue
        ex['archivo_gif'],ex['secuencia_animacion']=save_gif(ex)
        generated+=1
    (ROOT/'ejercicios.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"GIF generados: {generated}")
