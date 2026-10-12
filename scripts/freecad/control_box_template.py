"""Native, editable FreeCAD control-box demonstration. All dimensions are mm."""
import os
import math
import json
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore, QtWidgets

OUT = None
FRAMES = None
doc = None
base = None
lid = None
hardware = None
timer = None
NAVY = (0.24, 0.35, 0.49)
SILVER = (0.78, 0.82, 0.86)

def expr(obj, prop, value):
    obj.setExpression(prop, value)

def style(obj, color=NAVY):
    color = tuple(float(channel) for channel in color)
    obj.ViewObject.ShapeColor = color
    if not obj.Shape.isNull():
        obj.ViewObject.DiffuseColor = [color]*len(obj.Shape.Faces)
    obj.ViewObject.LineColor = (0.10, 0.13, 0.17)
    obj.ViewObject.DisplayMode = 'Flat Lines'
    obj.ViewObject.LineWidth = 1.5
    obj.ViewObject.AngularDeflection = 10
    obj.ViewObject.Deviation = 0.10

def show_only(objects):
    for obj in doc.Objects:
        if hasattr(obj, 'Shape'):
            obj.Visibility = obj in objects
    Gui.Selection.clearSelection()
    doc.recompute()
    for obj in objects:
        style(obj, SILVER if obj.Name=='Lid' else NAVY)
    Gui.updateGui()

def frame(name):
    Gui.updateGui()
    Gui.activeDocument().activeView().saveImage(os.path.join(FRAMES, name+'.png'), 1600, 1200, 'Current')

def init(output_directory, document_name='AI_ControlBox_Demo'):
    global doc, OUT, FRAMES
    if not os.path.isabs(output_directory):
        raise ValueError('Use an explicit absolute output directory')
    if document_name in App.listDocuments():
        raise RuntimeError('Document already exists; preserve and inspect it.')
    OUT = output_directory
    FRAMES = os.path.join(OUT, 'design-views')
    os.makedirs(FRAMES, exist_ok=True)
    doc = App.newDocument(document_name)
    doc.Label = 'Control Box | editable concept'
    Gui.activateWorkbench('PartWorkbench')
    for dock in Gui.getMainWindow().findChildren(QtWidgets.QDockWidget):
        if dock.windowTitle() in ('Report view', 'Python console', 'Selection view'):
            dock.hide()
    dims = doc.addObject('Spreadsheet::Sheet', 'Dimensions')
    dims.Label = 'Dimensions (mm) - edit values here'
    dims.set('A1','CONTROL BOX / CONCEPT'); dims.set('A2','Parameter'); dims.set('B2','mm')
    values = [('BoxLength',140),('BoxWidth',90),('BoxHeight',50),('Wall',3),('LidThickness',3),
              ('IndicatorDiameter',8),('SwitchDiameter',16),('ScrewClearance',3.4),
              ('PilotDiameter',2.6),('PostDiameter',8),('CableDiameter',12)]
    for row,(alias,value) in enumerate(values,3):
        dims.set('A'+str(row), alias); dims.set('B'+str(row),str(value)+' mm'); dims.setAlias('B'+str(row),alias)
    dims.setColumnWidth('A',235); dims.setColumnWidth('B',85)
    dims.set('A15','Nominal demo dimensions'); dims.set('A16','Match real hardware before manufacture')
    doc.recompute()
    return {'document':doc.Name,'parameters':dict(values)}

def box(name, length, width, height, z):
    o=doc.addObject('Part::Box',name)
    for prop,value in [('Length',length),('Width',width),('Height',height),
                       ('Placement.Base.x','-('+length+')/2'),('Placement.Base.y','-('+width+')/2'),('Placement.Base.z',z)]:
        expr(o,prop,value)
    doc.recompute(); style(o)
    return o

def round_vertical(name, source, radius):
    o=doc.addObject('Part::Fillet',name); o.Base=source
    vertical=[]
    for i,edge in enumerate(source.Shape.Edges,1):
        v=edge.Vertexes
        if len(v)==2 and abs(v[0].Point.x-v[1].Point.x)<1e-7 and abs(v[0].Point.y-v[1].Point.y)<1e-7:
            vertical.append((i,radius,radius))
    o.Edges=vertical; doc.recompute(); style(o); source.Visibility=False
    return o

def cylinder(name, diameter, height, x, y, z):
    o=doc.addObject('Part::Cylinder',name)
    for prop,value in [('Radius','('+diameter+')/2'),('Height',height),
                       ('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:
        expr(o,prop,value)
    style(o); return o

def cut(name, a, b):
    o=doc.addObject('Part::Cut',name); o.Base=a; o.Tool=b; o.Refine=True
    doc.recompute(); style(o); a.Visibility=False; b.Visibility=False
    return o

def fusion(name, objects):
    o=doc.addObject('Part::MultiFuse',name); o.Shapes=objects; o.Refine=True
    doc.recompute(); style(o)
    for obj in objects: obj.Visibility=False
    return o

def outside():
    global base
    o=box('OuterBlock','Dimensions.BoxLength','Dimensions.BoxWidth','Dimensions.BoxHeight','0 mm')
    base=round_vertical('RoundedOutside',o,7)
    base.Label='01 / Rounded outer shell'
    assert base.Shape.isValid() and abs(base.Shape.BoundBox.XLength-140)<0.01
    show_only([base]); Gui.activeDocument().activeView().viewAxonometric(); Gui.activeDocument().activeView().fitAll()
    frame('01-outer-shell')

def hollow():
    global base
    inner=box('InnerCavity','Dimensions.BoxLength-2*Dimensions.Wall','Dimensions.BoxWidth-2*Dimensions.Wall','Dimensions.BoxHeight','Dimensions.Wall')
    inner_round=round_vertical('RoundedCavity',inner,4)
    base=cut('HollowShell',base,inner_round); base.Label='02 / Hollow shell - 3 mm walls'
    show_only([base]); frame('02-hollow-shell')

def supports():
    global base
    posts=[]; pilots=[]
    for i,(sx,sy) in enumerate([(-1,-1),(1,-1),(1,1),(-1,1)],1):
        x=str(sx)+'*(Dimensions.BoxLength/2-10 mm)';y=str(sy)+'*(Dimensions.BoxWidth/2-10 mm)'
        posts.append(cylinder('LidPost'+str(i),'Dimensions.PostDiameter','Dimensions.BoxHeight-Dimensions.Wall',x,y,'Dimensions.Wall'))
        pilots.append(cylinder('PilotHole'+str(i),'Dimensions.PilotDiameter','13 mm',x,y,'Dimensions.BoxHeight-12 mm'))
    posts_body=fusion('ShellWithPosts',[base]+posts)
    holes=fusion('PilotHoleTools',pilots)
    pre_base=cut('ShellWithPilotHoles',posts_body,holes)
    cable=cylinder('CableEntryTool','Dimensions.CableDiameter','10 mm','0 mm','-Dimensions.BoxWidth/2-5 mm','20 mm')
    cable.Placement.Rotation=App.Rotation(App.Vector(0,0,1),App.Vector(0,1,0))
    base=cut('Base',pre_base,cable); base.Label='BASE / cable entry + four screw posts'
    show_only([base]); frame('03-screw-posts-and-cable-entry')

def lid_holes():
    global lid
    blank=box('LidBlank','Dimensions.BoxLength','Dimensions.BoxWidth','Dimensions.LidThickness','Dimensions.BoxHeight+0.3 mm')
    rounded=round_vertical('RoundedLid',blank,7)
    holes=[]
    for i,x in enumerate([-28,0,28],1):
        holes.append(cylinder('IndicatorHole'+str(i),'Dimensions.IndicatorDiameter','Dimensions.LidThickness+2 mm',str(x)+' mm','16 mm','Dimensions.BoxHeight-0.7 mm'))
    for i,x in enumerate([-24,24],1):
        holes.append(cylinder('SwitchHole'+str(i),'Dimensions.SwitchDiameter','Dimensions.LidThickness+2 mm',str(x)+' mm','-18 mm','Dimensions.BoxHeight-0.7 mm'))
    for i,(sx,sy) in enumerate([(-1,-1),(1,-1),(1,1),(-1,1)],1):
        holes.append(cylinder('LidScrewHole'+str(i),'Dimensions.ScrewClearance','Dimensions.LidThickness+2 mm',str(sx)+'*(Dimensions.BoxLength/2-10 mm)',str(sy)+'*(Dimensions.BoxWidth/2-10 mm)','Dimensions.BoxHeight-0.7 mm'))
    tools=fusion('LidHoleTools',holes)
    lid=cut('Lid',rounded,tools); lid.Label='LID / 3 indicator holes + 2 switch holes'; style(lid,SILVER)
    show_only([base,lid]); Gui.activeDocument().activeView().fitAll(); frame('04-lid-with-holes')

def resize_switches(diameter):
    doc.Dimensions.set('B9',str(diameter)+' mm');doc.recompute();Gui.updateGui()
    assert abs(doc.SwitchHole1.Radius.Value-diameter/2)<0.001

def explode(offset=32):
    lid.Placement.Base.z=offset
    Gui.activeDocument().activeView().fitAll();Gui.updateGui();frame('05-exploded')

def assemble():
    lid.Placement.Base.z=0;Gui.activeDocument().activeView().fitAll();Gui.updateGui()

def preview_part(name, shape, color):
    o=doc.addObject('Part::Feature',name);o.Shape=shape;style(o,color)
    hardware.addObject(o)
    o.addProperty('App::PropertyString','Purpose','Concept').Purpose='Illustration only; verify purchased components separately.'
    return o

def populated():
    global hardware
    hardware=doc.addObject('App::DocumentObjectGroup','IllustrativeHardware')
    hardware.Label='Illustrative hardware / excluded from manufacturing exports'
    z=53.3
    for i,(x,color) in enumerate(zip([-28,0,28],[(0.12,0.76,0.42),(1.0,0.62,0.12),(0.90,0.16,0.18)]),1):
        ring=Part.makeCylinder(5.4,1.4,App.Vector(x,16,z)).cut(Part.makeCylinder(3.9,2,App.Vector(x,16,z)))
        preview_part('IndicatorBezel'+str(i),ring,(0.58,0.63,0.68))
        preview_part('IndicatorLens'+str(i),Part.makeCylinder(3.9,2.7,App.Vector(x,16,z)),color)
    for i,(x,color) in enumerate(zip([-24,24],[(0.13,0.18,0.23),(0.12,0.55,0.68)]),1):
        ring=Part.makeCylinder(10,1.6,App.Vector(x,-18,z)).cut(Part.makeCylinder(7.8,2,App.Vector(x,-18,z)))
        preview_part('SwitchBezel'+str(i),ring,(0.48,0.53,0.58))
        preview_part('SwitchButton'+str(i),Part.makeCylinder(7.8,3.8,App.Vector(x,-18,z)),color)
    for i,(x,y) in enumerate([(-60,-35),(60,-35),(60,35),(-60,35)],1):
        screw=Part.makeCylinder(2.9,1.2,App.Vector(x,y,z))
        slot=Part.makeBox(4.4,0.8,0.7,App.Vector(x-2.2,y-0.4,z+0.7))
        preview_part('IllustrativeScrew'+str(i),screw.cut(slot),(0.43,0.47,0.52))
    # Flat panel lettering is display artwork, rather than manufactured engraving.
    import Draft
    for text,x,y,size in [('CONTROL / 01',0,30,3.6),('READY',-28,6,2.2),('RUN',0,6,2.2),('ALERT',28,6,2.2),('POWER',-24,-33,2.6),('MODE',24,-33,2.6)]:
        label=Draft.make_shapestring(String=text,FontFile=r'C:\Windows\Fonts\arial.ttf',Size=size,Tracking=0)
        doc.recompute();bb=label.Shape.BoundBox
        label.Placement.Base=App.Vector(x-bb.XLength/2,y,z+0.03)
        label.Label='Panel artwork / '+text; label.ViewObject.ShapeColor=(0.08,0.14,0.20); hardware.addObject(label)
    doc.recompute();style(base,NAVY);style(lid,SILVER);Gui.Selection.clearSelection();Gui.activeDocument().activeView().fitAll();frame('06-assembled-concept')

def turntable(seconds=6):
    global timer
    view=Gui.activeDocument().activeView();rotation=view.getCameraOrientation();frames=max(1,int(seconds*30));counter=[0]
    timer=QtCore.QTimer()
    def tick():
        counter[0]+=1
        fraction=min(1.0,counter[0]/float(frames));eased=0.5-0.5*math.cos(math.pi*fraction)
        view.setCameraOrientation(App.Rotation(App.Vector(0,0,1),60*eased).multiply(rotation).Q)
        if counter[0]>=frames:timer.stop()
    timer.timeout.connect(tick);timer.start(33)

def verify_export():
    from pathlib import Path
    import MeshPart
    doc.recompute()
    checks={}
    for obj in [base,lid]:
        checks[obj.Name]={'valid':obj.Shape.isValid(),'solids':len(obj.Shape.Solids),'volume_mm3':obj.Shape.Volume,'bounds_mm':[obj.Shape.BoundBox.XLength,obj.Shape.BoundBox.YLength,obj.Shape.BoundBox.ZLength]}
        assert checks[obj.Name]['valid'] and checks[obj.Name]['solids']==1
    assert base.Shape.common(lid.Shape).Volume<1e-6
    if os.path.exists(os.path.join(OUT,'Control-Box-v1.FCStd')):
        raise RuntimeError('Existing export preserved; choose a new output directory/version')
    doc.saveAs(os.path.join(OUT,'Control-Box-v1.FCStd'))
    Part.export([base,lid],os.path.join(OUT,'Control-Box-v1.step'))
    for obj,name in [(base,'Base'),(lid,'Lid')]:
        mesh=MeshPart.meshFromShape(Shape=obj.Shape,LinearDeflection=0.08,AngularDeflection=0.15,Relative=False)
        mesh.translate(0,0,-mesh.BoundBox.ZMin)
        mesh.write(os.path.join(OUT,'Control-Box-'+name+'-v1.stl'))
    checks['switch_holes_mm']=doc.SwitchHole1.Radius.Value*2
    checks['indicator_holes_mm']=doc.IndicatorHole1.Radius.Value*2
    checks['base_lid_intersection_mm3']=base.Shape.common(lid.Shape).Volume
    checks['manufacturing_status']='Concept geometry validated; physical fit, tolerances and electrical suitability not tested.'
    Path(os.path.join(OUT,'MODEL-CHECKS.json')).write_text(json.dumps(checks,indent=2),encoding='utf-8')
    frame('07-final-view');return checks

