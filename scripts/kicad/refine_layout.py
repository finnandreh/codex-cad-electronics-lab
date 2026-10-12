from pathlib import Path
import os,json,shutil
ROOT=Path(os.environ.get('CAD_LAB_WORKSPACE',Path.cwd())).resolve();OUT=Path(os.environ.get('CODEX_PULSE_OUT',ROOT/'build/Codex-Pulse-5V')).resolve();W=Path(__file__).resolve().parent
d=json.loads((OUT/'DESIGN.json').read_text())
for c in d['components']:
    if c['ref']=='R1':c['pcb']=[17.78,5.08]
    if c['ref']=='R4':c['pcb']=[6.35,25.4]
    if c['ref']=='D1':c['pcb']=[38.1,26.67]
(OUT/'DESIGN.json').write_text(json.dumps(d,indent=2))
share=Path(os.environ.get('KICAD_FOOTPRINTS','/usr/share/kicad/footprints'));families=set()
for path in [c['footprint'] for c in d['components'] if c['footprint']]+['MountingHole:MountingHole_3.2mm_M3']:
    family,item=path.split(':');families.add(family);folder=OUT/'footprints'/(family+'.pretty');folder.mkdir(parents=True,exist_ok=True);shutil.copy2(share/(family+'.pretty')/(item+'.kicad_mod'),folder/(item+'.kicad_mod'))
(OUT/'fp-lib-table').write_text('(fp_lib_table (version 7)\n'+'\n'.join('(lib (name '+json.dumps(f)+')(type "KiCad")(uri "${KIPRJMOD}/footprints/'+f+'.pretty")(options "")(descr "Project-local official KiCad7 footprint"))' for f in sorted(families))+'\n)')
defs=(W/'create_schematic.py').read_text().split("RFP='",1)[0];scope={ '__file__':str(W/'create_schematic.py') };exec(defs,scope);parse,dump,tag=scope['parse'],scope['dump'],scope['tag']
sch=OUT/'Codex-Pulse-5V.kicad_sch';before=sch.read_text();root=parse(before)
for inst in root:
    if not isinstance(inst,list) or inst[0]!='symbol' or not tag(inst,'lib_id'):continue
    ref=next(x[2] for x in inst if isinstance(x,list) and x[0]=='property' and x[1]=='Reference');at=tag(inst,'at');x,y=float(at[1]),float(at[2])
    for prop in inst:
        if not isinstance(prop,list) or prop[0]!='property' or prop[1] not in ('Reference','Value'):continue
        if ref[0] in 'RC':px,py=x+4.5,y+(-2 if prop[1]=='Reference' else 2)
        elif ref=='U1':px,py=x-18,y+(-20 if prop[1]=='Reference' else -17)
        else:continue
        a=tag(prop,'at');a[1:]=[scope['Atom'](str(px)),scope['Atom'](str(py)),scope['Atom']('0')]
        effects=tag(prop,'effects');j=tag(effects,'justify')
        if j:j[1:]=[scope['Atom']('left')]
        else:effects.append([scope['Atom']('justify'),scope['Atom']('left')])
history=W/'schematic-before-layout-refinement.kicad_sch';assert not history.exists();history.write_text(before);sch.write_text(dump(root))
for source,dest in [(OUT/'Codex-Pulse-5V.kicad_pcb',W/'routed-before-courtyard-refinement.kicad_pcb'),(OUT/'DRC-v1.txt',OUT/'DRC-before-refinement.txt')]:
    assert source.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve()) and not dest.exists();source.rename(dest)
print('Placed R1/R4/LED clear of courtyard overlaps; local footprint libraries and readable schematic labels updated')
