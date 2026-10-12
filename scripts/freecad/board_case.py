"""Editable FreeCAD enclosure. Official sources live in each public spec."""
import os,json
import FreeCAD as App, FreeCADGui as Gui, Part, MeshPart
from PySide import QtCore,QtWidgets
import control_box_template as cb
V=App.Vector
doc=None;base=None;lid=None;board=None;timer=None;board_art=None

def box(name,l,w,h,x,y,z):
    o=doc.addObject('Part::Box',name)
    for prop,value in [('Length',l),('Width',w),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:o.setExpression(prop,str(value))
    doc.recompute();return o

def frame(name):
    Gui.updateGui();Gui.activeDocument().activeView().saveImage(os.path.join(OUT,'design-views',name+'.png'),1600,1200,'Current')

def show(objects,reference=False):
    for o in doc.Objects:
        if hasattr(o,'Shape'):o.Visibility=o in objects or (o==board and reference)
    for o in objects:cb.style(o,(.82,.86,.90) if o==lid else tuple(C['color']))
    if board_art:board_art.Visibility=reference
    Gui.Selection.clearSelection();doc.recompute();Gui.updateGui()

def init(config, output_directory=None):
    global C,OUT,doc,board,L,W,corner,board_art
    C=json.load(open(config,encoding='utf-8'));OUT=output_directory or C.get('output');L=C['length'];W=C['width'];board_art=None
    if not OUT or not os.path.isabs(OUT):raise ValueError('Pass an explicit absolute output directory')
    os.makedirs(os.path.join(OUT,'design-views'),exist_ok=True)
    name=C['document']
    if name in App.listDocuments():raise RuntimeError('Preserve existing document '+name)
    doc=App.newDocument(name);doc.Label=C['name']+' | editable case'
    cb.doc=doc;Gui.activateWorkbench('PartWorkbench')
    for dock in Gui.getMainWindow().findChildren(QtWidgets.QDockWidget):
        if dock.windowTitle() in ('Report view','Python console','Selection view'):dock.hide()
    d=doc.addObject('Spreadsheet::Sheet','Dimensions');d.Label='EDIT dimensions in millimetres'
    vals=[('BoardLength',L),('BoardWidth',W),('PCBThickness',C['pcb_thickness']),('BoardTop',C.get('board_top',8)),('CaseLength',C.get('case_length',L+16)),('CaseWidth',C.get('case_width',W+16)),('CaseHeight',C.get('height',18)),('Wall',2.4),('Floor',2.4),('LidThickness',2.4),('LidGap',.25),('LidPilot',2.5),('LidClearance',3.2)]
    for row,(alias,value) in enumerate(vals,2):
        d.set('A'+str(row),alias);d.set('B'+str(row),str(value)+' mm');d.setAlias('B'+str(row),alias)
    d.setColumnWidth('A',220);d.setColumnWidth('B',115)
    d.set('A17','Reference: '+C['source_credit']);d.set('A18','Physical fit and RF/thermal tests pending')
    board=doc.addObject('Part::Feature','BoardReference')
    if C.get('step'):
        shape=Part.read(C['step']);shape.rotate(V(0,0,0),V(0,0,1),C.get('step_rotation',0));shape.translate(V(*C.get('step_translate',[0,0,0])))
        board.Shape=shape;board.Label=C['board_name']+' | official STEP reference'
    else:
        board.Shape=Part.makeBox(L,W,C['pcb_thickness'],V(0,0,-C['pcb_thickness']))
        board.Label=C['board_name']+' | simplified dimensional envelope'
    board.Placement.Base.z=C.get('board_top',8);cb.style(board,(.10,.40,.27))
    if C.get('step'):
        colors=[]
        for solid in board.Shape.Solids:
            bb=solid.BoundBox
            color=(.08,.43,.34) if bb.XLength>L*.85 and bb.YLength>W*.85 and bb.ZLength<2 else (.72,.74,.76) if bb.XMin<3 else (.78,.64,.26) if min(bb.XLength,bb.YLength)<1 else (.17,.19,.21)
            colors.extend([color]*len(solid.Faces))
        if len(colors)==len(board.Shape.Faces):board.ViewObject.DiffuseColor=colors
    if C.get('board_image'):
        board_art=doc.addObject('Image::ImagePlane','BoardIllustration');board_art.Label='Official board artwork / flat visual reference';board_art.ImageFile=C['board_image'];board_art.XSize=C.get('board_image_length',L);board_art.YSize=C.get('board_image_width',W);board_art.Placement.Base=V(*C.get('board_image_center',[L/2,W/2,C.get('board_top',8)+.03]));board_art.Placement.Rotation=App.Rotation(V(0,0,1),C.get('board_image_rotation',0))
        board_art.addProperty('App::PropertyString','Representation');board_art.Representation='Flat manufacturer illustration; component heights not represented; excluded from manufacturing exports'
    for prop,text in [('ReferenceSource',C['source_url']),('Representation','Official STEP' if C.get('step') else 'Simplified board envelope; connectors are design allowances, not measured component geometry'),('Manufacturing','Excluded from case STEP/STL exports')]:
        board.addProperty('App::PropertyString',prop,'Reference');setattr(board,prop,text)
    corner=C.get('lid_posts',[(-4,-4),(L+4,-4),(L+4,W+4),(-4,W+4)])
    show([],True);Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll();frame('00-board-reference')
    return {'document':name,'board_mm':[L,W],'reference':board.Label}

def shell():
    global base
    outer=box('OuterBlank','Dimensions.CaseLength','Dimensions.CaseWidth','Dimensions.CaseHeight',-8,-8,0)
    base=cb.round_vertical('RoundedShell',outer,3.8);base.Label='01 / rounded outside'
    show([base]);Gui.activeDocument().activeView().fitAll();frame('01-outside')

def hollow():
    global base
    cavity=box('Cavity','Dimensions.CaseLength-2*Dimensions.Wall','Dimensions.CaseWidth-2*Dimensions.Wall','Dimensions.CaseHeight','-8 mm+Dimensions.Wall','-8 mm+Dimensions.Wall','Dimensions.Floor')
    cavity=cb.round_vertical('RoundedCavity',cavity,1.4)
    base=cb.cut('HollowShell',base,cavity);base.Label='02 / 2.4 mm walls and floor'
    show([base]);frame('02-hollow')

def supports():
    global base
    posts=[];holes=[]
    for i,(x,y) in enumerate(C.get('mounts',[])):
        posts.append(cb.cylinder('BoardSupport'+str(i),str(C.get('post_diameter',2.8))+' mm','Dimensions.BoardTop-Dimensions.PCBThickness-Dimensions.Floor+0.2 mm',str(x)+' mm',str(y)+' mm','Dimensions.Floor-0.2 mm'))
        holes.append(cb.cylinder('BoardPilot'+str(i),str(C.get('board_pilot',1.1))+' mm','Dimensions.BoardTop',str(x)+' mm',str(y)+' mm','Dimensions.Floor'))
    for i,(x,y) in enumerate(C.get('rests',[])):
        posts.append(box('BoardRest'+str(i),C.get('rest_length',5),C.get('rest_width',1.4),'Dimensions.BoardTop-Dimensions.PCBThickness-Dimensions.Floor+0.2 mm',x,y,'Dimensions.Floor-0.2 mm'))
    for i,(x,y) in enumerate(corner):
        posts.append(cb.cylinder('LidPost'+str(i),'6.2 mm','Dimensions.CaseHeight-Dimensions.Floor+0.2 mm',str(x)+' mm',str(y)+' mm','Dimensions.Floor-0.2 mm'))
        holes.append(cb.cylinder('LidPilot'+str(i),'Dimensions.LidPilot','10 mm',str(x)+' mm',str(y)+' mm','Dimensions.CaseHeight-9 mm'))
    base=cb.cut('SupportedBase',cb.fusion('ShellAndSupports',[base]+posts),cb.fusion('PilotTools',holes));base.Label='03 / board supports and lid screw posts'
    show([base]);frame('03-supports')

def ports():
    global base
    tools=[]
    for i,p in enumerate(C['ports']):tools.append(box('PortAllowance'+str(i),*p))
    base=cb.cut('CaseBase',base,tools[0] if len(tools)==1 else cb.fusion('ConnectorOpeningTools',tools));base.Label='BASE / connector and cable access'
    show([base],True);frame('04-ports-and-board')

def panel():
    global lid
    blank=box('LidBlank','Dimensions.CaseLength','Dimensions.CaseWidth','Dimensions.LidThickness',-8,-8,'Dimensions.CaseHeight+Dimensions.LidGap')
    rounded=cb.round_vertical('RoundedLid',blank,3.8);tools=[]
    for i,(x,y,l,w) in enumerate(C['lid_windows']):tools.append(box('AccessWindow'+str(i),l,w,'Dimensions.LidThickness+2 mm',x,y,'Dimensions.CaseHeight+Dimensions.LidGap-1 mm'))
    for i,(x,y) in enumerate(corner):
        tools.append(cb.cylinder('LidHole'+str(i),'Dimensions.LidClearance','Dimensions.LidThickness+2 mm',str(x)+' mm',str(y)+' mm','Dimensions.CaseHeight+Dimensions.LidGap-1 mm'))
        tools.append(cb.cylinder('ScrewRecess'+str(i),'5.8 mm','2 mm',str(x)+' mm',str(y)+' mm','Dimensions.CaseHeight+Dimensions.LidGap+Dimensions.LidThickness-1 mm'))
    lid=cb.cut('CaseLid',rounded,cb.fusion('LidAccessTools',tools));lid.Label='LID / headers, controls and ventilation'
    show([base,lid],True);Gui.activeDocument().activeView().fitAll();frame('05-assembled')

def top():Gui.activeDocument().activeView().viewTop();frame('06-top')
def explode():
    board.Placement.Base.z=C.get('board_top',8);lid.Placement.Base.z=32
    if board_art:board_art.Placement.Base.z=C.get('board_top',8)+.03
    Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll();frame('07-exploded')
def assemble():
    board.Placement.Base.z=C.get('board_top',8);lid.Placement.Base.z=0
    if board_art:board_art.Placement.Base.z=C.get('board_top',8)+.03
    show([base,lid],True);Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll();frame('08-finished')
def turntable():
    global timer
    view=Gui.activeDocument().activeView();start=view.getCameraOrientation();tick=[0]
    def step():
        tick[0]+=1;view.setCameraOrientation(App.Rotation(V(0,0,1),tick[0]*2).multiply(start).Q)
        if tick[0]>=80:timer.stop()
    timer=QtCore.QTimer();timer.timeout.connect(step);timer.start(70)

def export():
    assemble();checks={}
    for label,o in [('base',base),('lid',lid)]:
        assert o.Shape.isValid() and len(o.Shape.Solids)==1,(label,len(o.Shape.Solids))
        checks[label+'_valid']=True
    checks['base_lid_intersection_mm3']=base.Shape.common(lid.Shape).Volume
    checks['base_board_intersection_mm3']=base.Shape.common(board.Shape).Volume
    checks['lid_board_intersection_mm3']=lid.Shape.common(board.Shape).Volume
    assert max(checks[k] for k in checks if k.endswith('mm3'))<1e-5,checks
    native=os.path.join(OUT,C['name']+'-v1.FCStd')
    if os.path.exists(native):raise RuntimeError('Preserve existing output')
    doc.recompute();doc.saveAs(native);Part.export([base,lid],os.path.join(OUT,C['name']+'-v1.step'))
    for label,o in [('Base',base),('Lid',lid)]:
        shape=o.Shape.copy();shape.translate(V(0,0,-shape.BoundBox.ZMin))
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.18,Relative=False)
        mesh.removeDuplicatedPoints();mesh.removeDuplicatedFacets();mesh.harmonizeNormals();assert mesh.isSolid()
        mesh.write(os.path.join(OUT,C['name']+'-'+label+'-v1.stl'))
    checks.update(native=native,case_envelope_mm=[C.get('case_length',L+16),C.get('case_width',W+16),C.get('height',18)+2.65],reference=board.Label,source=C['source_url'],physical_fit='Not tested; verify real board, screws, cable, printing tolerances and RF/thermal behaviour',reference_excluded_from_case_exports=True)
    open(os.path.join(OUT,'MODEL-CHECKS.json'),'w').write(json.dumps(checks,indent=2));frame('09-exported');return checks
