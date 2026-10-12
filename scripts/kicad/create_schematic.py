from pathlib import Path
import os,re,json,uuid,copy,csv,urllib.request,hashlib
ROOT=Path(os.environ.get('CAD_LAB_WORKSPACE',Path.cwd())).resolve()
OUT=Path(os.environ.get('CODEX_PULSE_OUT',ROOT/'build/Codex-Pulse-5V')).resolve();OUT.mkdir(parents=True,exist_ok=True)
NAME='Codex-Pulse-5V';SHARE=Path(os.environ.get('KICAD_7_SHARE','/usr/share/kicad'))
class Atom(str):pass
def parse(text):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text);stack=[];root=None
    for t in tokens:
        if t=='(':
            a=[]
            if stack:stack[-1].append(a)
            else:root=a
            stack.append(a)
        elif t==')':stack.pop()
        else:stack[-1].append(json.loads(t) if t.startswith('"') else Atom(t))
    assert not stack;return root
def dump(a):return '('+' '.join(dump(x) for x in a)+')' if isinstance(a,list) else str(a) if isinstance(a,Atom) else json.dumps(a,ensure_ascii=False)
def tag(a,k):return next((x for x in a if isinstance(x,list) and x[0]==k),None)
def uid():return str(uuid.uuid4())
libraries={}
def symbol(lib,name):
    if lib not in libraries:
        root=parse((SHARE/'symbols'/(lib+'.kicad_sym')).read_text(encoding='utf-8'));libraries[lib]={x[1]:x for x in root if isinstance(x,list) and x[0]=='symbol'}
    s=copy.deepcopy(libraries[lib][name]);ex=tag(s,'extends')
    if ex:
        base=symbol(lib,ex[1]);props={p[1]:p for p in base if isinstance(p,list) and p[0]=='property'}
        props.update({p[1]:p for p in s if isinstance(p,list) and p[0]=='property'})
        children=[x for x in base[2:] if isinstance(x,list) and x[0]!='property']
        for x in children:
            if x[0]=='symbol':x[1]=x[1].replace(base[1]+'_',name+'_',1)
        s=[Atom('symbol'),name]+list(props.values())+children
    return s
RFP='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal'
CFP='Capacitor_THT:C_Radial_D5.0mm_H11.0mm_P2.00mm'
DFP='Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm'
components=[
dict(ref='U1',value='TLC555CP',lib='Timer',sym='TLC555xP',footprint='Package_DIP:DIP-8_W7.62mm',schematic=[120,85],pcb=[22.86,12.7],pins={'1':'GND','2':'TIMING','3':'OUT','4':'RESET','5':'CTRL','6':'TIMING','7':'DISCH','8':'+5V'},datasheet='https://www.ti.com/lit/ds/symlink/tlc555.pdf'),
dict(ref='J1',value='5V INPUT',lib='Connector_Generic',sym='Conn_01x02',footprint='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',schematic=[40,45],pcb=[7.62,10.16],pins={'1':'+5V','2':'GND'}),
dict(ref='R1',value='10k',lib='Device',sym='R',footprint=RFP,schematic=[175,55],pcb=[35.56,5.08],pins={'1':'+5V','2':'DISCH'}),
dict(ref='R2',value='100k',lib='Device',sym='R',footprint=RFP,schematic=[175,85],pcb=[35.56,11.43],pins={'1':'DISCH','2':'TIMING'}),
dict(ref='R3',value='1k',lib='Device',sym='R',footprint=RFP,schematic=[220,70],pcb=[33.02,31.75],pins={'1':'OUT','2':'LED_A'}),
dict(ref='R4',value='10k',lib='Device',sym='R',footprint=RFP,schematic=[45,135],pcb=[7.62,25.4],pins={'1':'+5V','2':'RESET'}),
dict(ref='C1',value='10uF 16V',lib='Device',sym='C_Polarized',footprint=CFP,schematic=[175,115],pcb=[40.64,19.05],pins={'1':'TIMING','2':'GND'}),
dict(ref='C2',value='100nF',lib='Device',sym='C',footprint=DFP,schematic=[70,55],pcb=[30.48,7.62],pins={'1':'+5V','2':'GND'}),
dict(ref='C3',value='10nF',lib='Device',sym='C',footprint=DFP,schematic=[75,115],pcb=[29.21,26.67],pins={'1':'CTRL','2':'GND'}),
dict(ref='C4',value='10uF 16V',lib='Device',sym='C_Polarized',footprint=CFP,schematic=[45,90],pcb=[10.16,17.78],pins={'1':'+5V','2':'GND'}),
dict(ref='SW1',value='RESET',lib='Switch',sym='SW_Push',footprint='Button_Switch_THT:SW_PUSH_6mm',schematic=[85,145],pcb=[17.78,26.67],pins={'1':'RESET','2':'GND'}),
dict(ref='D1',value='RED LED',lib='Device',sym='LED',footprint='LED_THT:LED_D5.0mm',schematic=[220,100],pcb=[40.64,26.67],pins={'1':'GND','2':'LED_A'}),
dict(ref='#FLG01',value='PWR_FLAG',lib='power',sym='PWR_FLAG',footprint='',schematic=[40,170],pins={'1':'+5V'}),
dict(ref='#FLG02',value='PWR_FLAG',lib='power',sym='PWR_FLAG',footprint='',schematic=[75,170],pins={'1':'GND'})]
root_id=uid();body=[];embedded={}
for c in components:
    c['uuid']=uid();libid=c['lib']+':'+c['sym'];s=symbol(c['lib'],c['sym']);emb=copy.deepcopy(s);emb[1]=libid;embedded[libid]=emb
    pins=[]
    for sub in s:
        if isinstance(sub,list) and sub[0]=='symbol':pins.extend(x for x in sub if isinstance(x,list) and x[0]=='pin')
    x,y=c['schematic'];inst=[Atom('symbol'),[Atom('lib_id'),libid],[Atom('at'),Atom(str(x)),Atom(str(y)),Atom('0')],[Atom('unit'),Atom('1')],[Atom('in_bom'),Atom('no' if c['ref'].startswith('#') else 'yes')],[Atom('on_board'),Atom('no' if c['ref'].startswith('#') else 'yes')],[Atom('dnp'),Atom('no')],[Atom('uuid'),Atom(c['uuid'])]]
    for key,value,dy,hidden in [('Reference',c['ref'],-14,False),('Value',c['value'],-11,False),('Footprint',c['footprint'],0,True),('Datasheet',c.get('datasheet',''),0,True)]:
        effects=[Atom('effects'),[Atom('font'),[Atom('size'),Atom('1.27'),Atom('1.27')]]]
        if hidden:effects.append(Atom('hide'))
        inst.append([Atom('property'),key,value,[Atom('at'),Atom(str(x)),Atom(str(y+dy)),Atom('0')],effects])
    import math
    for pin in pins:
        number=tag(pin,'number')[1];assert number in c['pins'];a=tag(pin,'at');px=x+float(a[1]);py=y-float(a[2]);ang=math.radians(float(a[3]));ex=round(px-5.08*math.cos(ang),4);ey=round(py+5.08*math.sin(ang),4)
        body.append(parse(f'(wire (pts (xy {px} {py}) (xy {ex} {ey})) (stroke (width 0) (type default)) (uuid {uid()}))'))
        body.append(parse(f'(label {json.dumps(c["pins"][number])} (at {ex} {ey} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uid()}))'))
        inst.append([Atom('pin'),number,[Atom('uuid'),Atom(uid())]])
    inst.append(parse(f'(instances (project "{NAME}" (path "/{root_id}" (reference "{c["ref"]}") (unit 1))))'));body.append(inst)
top=parse(f'(kicad_sch (version 20230121) (generator eeschema) (uuid {root_id}) (paper "A4") (title_block (title "Codex Pulse: 5 V LED timer") (date "2026-10-12") (rev "1.0 prototype") (company "finnandre.no") (comment 1 "Designed with OpenAI Codex / physical test pending")))')
top.append([Atom('lib_symbols')]+list(embedded.values()));top+=body
for x,y,text in [(30,20,'5 V LED pulse board / TLC555 CMOS timer'),(100,25,'Nominal 0.69 Hz / about 52 percent on'),(30,190,'5 V regulated supply only. Confirm polarity. Prototype: physical build and validation pending.'),(140,145,'R1 10k / R2 100k / C1 10uF'),(140,151,'f = 1.44 / ((R1 + 2 R2) C1)'),(140,157,'TI TLC555 Rev K: astable reference and pinout')]:
    top.append(parse(f'(text {json.dumps(text)} (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid {uid()}))'))
dest=OUT/(NAME+'.kicad_sch');assert not dest.exists();dest.write_text(dump(top),encoding='utf-8')
project=dict(meta=dict(filename=NAME+'.kicad_pro',version=1),board=dict(design_settings=dict(rules=dict(min_clearance=.25,min_track_width=.25,min_via_diameter=.6,min_through_hole_diameter=.3),net_settings=dict(classes=[dict(name='Default',description='Prototype 2-layer rules',clearance=.25,track_width=.3,via_diameter=.6,via_drill=.3)]))))
(OUT/(NAME+'.kicad_pro')).write_text(json.dumps(project,indent=2))
design=dict(name=NAME,schematic_uuid=root_id,components=components,board_mm=[50,35],supply_V=5,nominal_frequency_Hz=1.44/(210000*.00001),nominal_duty_percent=110000/210000*100,physical_test='Not performed',source='https://www.ti.com/lit/ds/symlink/tlc555.pdf',footprint_note='Stock KiCad7 through-hole footprints; verify exact purchased part lead spacing/body before fabrication')
(OUT/'DESIGN.json').write_text(json.dumps(design,indent=2))
with (OUT/'BOM.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['Reference','Value','Footprint','Notes'])
    for c in components:
        if c['footprint']:w.writerow([c['ref'],c['value'],c['footprint'],'TLC555CP CMOS, not bipolar substitution' if c['ref']=='U1' else 'Verify purchased component dimensions'])
pdf=Path(os.environ.get('TLC555_DATASHEET',ROOT/'references/TI-TLC555-RevK.pdf')).resolve()
pdf.parent.mkdir(parents=True,exist_ok=True)
if not pdf.exists():urllib.request.urlretrieve(design['source'],pdf)
(OUT/'SOURCE.json').write_text(json.dumps(dict(url=design['source'],local_reference=str(pdf),sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),revision='SLFS043K January2026',application='5V astable timing, standard8pinPDIP pinout'),indent=2))
print(json.dumps(dict(schematic=str(dest),components=12,nets=8,nominal_hz=design['nominal_frequency_Hz'])))
