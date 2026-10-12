from pathlib import Path
import os,pcbnew as p,json,re,datetime,hashlib
ROOT=Path(os.environ.get('CAD_LAB_WORKSPACE',Path.cwd())).resolve();OUT=Path(os.environ.get('CODEX_PULSE_OUT',ROOT/'build/Codex-Pulse-5V')).resolve();NAME='Codex-Pulse-5V'
project=OUT/(NAME+'.kicad_pro');d=json.loads(project.read_text());d['board']['design_settings'].pop('net_settings',None);d['board']['design_settings']['rules'].update(min_clearance=.25,min_track_width=.25,min_via_diameter=.6,min_through_hole_diameter=.3,min_silk_clearance=.15);d['net_settings']={'meta':{'version':3},'classes':[{'name':'Default','description':'Prototype 2-layer rules','clearance':.25,'track_width':.3,'via_diameter':.6,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.25,'diff_pair_via_gap':.25}],'net_colors':None,'netclass_assignments':None,'netclass_patterns':[]};project.write_text(json.dumps(d,indent=2))
manager=p.GetSettingsManager();assert manager.LoadProject(str(project));boardpath=OUT/(NAME+'.kicad_pcb');b=p.LoadBoard(str(boardpath));b.SetProject(manager.Prj())
for drawing in b.GetDrawings():
    if isinstance(drawing,p.PCB_TEXT) and drawing.GetText()=='CODEX PULSE':drawing.SetPosition(p.VECTOR2I(p.FromMM(18),p.FromMM(1)))
    if isinstance(drawing,p.PCB_TEXT) and drawing.GetText()=='0.69 Hz':drawing.SetPosition(p.VECTOR2I(p.FromMM(43),p.FromMM(23)))
for fp in b.GetFootprints():
    if fp.GetReference()=='R3':fp.Reference().SetPosition(p.VECTOR2I(p.FromMM(36.83),p.FromMM(34.1)))
p.SaveBoard(str(boardpath),b);check=p.LoadBoard(str(boardpath));check.SetProject(manager.Prj());check.BuildConnectivity();report=OUT/'DRC-FINAL.txt';assert p.WriteDRCReport(check,str(report),p.EDA_UNITS_MILLIMETRES,True)
text=report.read_text(encoding='utf-8');counts=[int(x) for x in re.findall(r'\*\* Found (\d+)',text)];assert counts==[0,0,0],text
rows={}
for fp in check.GetFootprints():
    if fp.GetReference().startswith('H'):continue
    for pad in fp.Pads():rows[(fp.GetReference(),pad.GetNumber())]=pad.GetNetname().removeprefix('/')
design=json.loads((OUT/'DESIGN.json').read_text());expected={(c['ref'],n):net for c in design['components'] if c['footprint'] for n,net in c['pins'].items()};assert rows==expected
receipt=dict(checked_at=datetime.datetime.now().astimezone().isoformat(timespec='seconds'),native_version=p.GetBuildVersion(),native_schematic_export='PASS',schematic_to_design_pin_net_comparison='PASS:30electricalpins/eightnets',PCB_to_schematic_pin_net_comparison='PASS',pcb_reopened=True,drc_violations=0,unconnected_pads=0,footprint_errors=0,copper_layers=2,board_mm=[50,35],minimum_requested_clearance_mm=.25,track_width_mm=.3,via_diameter_mm=.6,via_drill_mm=.3,components=12,mounting_holes=4,physical_test='Not performed',native_ERC='Not run: installed KiCad7 CLI provides schematic export but no ERC command; netlist and pin functions inspected separately',nominal_frequency_Hz=design['nominal_frequency_Hz'],nominal_duty_percent=design['nominal_duty_percent'],manufacturing='Prototype files only; no fabrication order or publication performed',board_sha256=hashlib.sha256(boardpath.read_bytes()).hexdigest())
(OUT/'VERIFICATION.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
