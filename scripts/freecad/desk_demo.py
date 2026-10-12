import math,os,json
import control_box_template as cb
from control_box_template import App,Gui,Part

N=App.Vector(0,-1,3);N.normalize()

def init(out):
    cb.init(out,'Sloped_Desktop_Control_v3')
    cb.doc.Label='Sloped Desktop Control / concept'
    cb.NAVY=(0.25,0.26,0.42)
    cb.doc.Dimensions.set('B5','55 mm');cb.doc.recompute()

def profile(name,points):
    import Sketcher
    sk=cb.doc.addObject('Sketcher::SketchObject',name)
    sk.Placement=App.Placement(App.Vector(-70,0,0),App.Rotation(App.Vector(1,1,1),120))
    sk.setExpression('Placement.Base.x','-Dimensions.BoxLength/2')
    for i,(y,z) in enumerate(points):
        yy,zz=points[(i+1)%len(points)]
        sk.addGeometry(Part.LineSegment(App.Vector(y,z,0),App.Vector(yy,zz,0)),False)
    cb.doc.recompute()
    ex=cb.doc.addObject('Part::Extrusion',name+'Extrusion');ex.Base=sk
    ex.DirMode='Custom';ex.Dir=App.Vector(1,0,0);ex.Solid=True
    ex.setExpression('LengthFwd','Dimensions.BoxLength')
    cb.doc.recompute();sk.Visibility=False;cb.style(ex)
    return ex

def outside():
    cb.base=profile('SlopedSideProfile',[(-45,0),(45,0),(45,55),(-45,25)])
    cb.base.Label='01 / Sloped enclosure - editable side sketch'
    cb.show_only([cb.base]);Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll();cb.frame('01-sloped-shell')

def hollow():
    inner=cb.box('InteriorTool','Dimensions.BoxLength-2*Dimensions.Wall','Dimensions.BoxWidth-2*Dimensions.Wall','70 mm','Dimensions.Wall')
    cb.base=cb.cut('HollowSlopedShell',cb.base,inner)
    cb.show_only([cb.base]);cb.frame('02-hollow')

def supports():
    posts=[];tools=[]
    for i,(x,y) in enumerate([(-60,-35),(60,-35),(60,35),(-60,35)],1):
        top=40+y/3
        posts.append(cb.cylinder('ScrewPost'+str(i),'8 mm',str(top-4.5)+' mm',str(x)+' mm',str(y)+' mm','3 mm'))
        tools.append(cb.cylinder('Pilot'+str(i),'2.6 mm','13 mm',str(x)+' mm',str(y)+' mm',str(top-12)+' mm'))
    body=cb.fusion('ShellWithScrewPosts',[cb.base]+posts)
    cb.base=cb.cut('SlopedBase',body,cb.fusion('PilotTools',tools))
    cable=cb.cylinder('RearCableTool','12 mm','10 mm','0 mm','40 mm','25 mm')
    cable.Placement.Rotation=App.Rotation(App.Vector(0,0,1),App.Vector(0,1,0))
    cb.base=cb.cut('Base',cb.base,cable);cb.base.Label='BASE / inclined rim + 4 screw posts'
    cb.show_only([cb.base]);cb.frame('03-supports-cable')

def hole(name,d,x,y):
    o=cb.cylinder(name,d,'12 mm',str(x)+' mm',str(y)+' mm',str(40.3+y/3)+' mm')
    o.Placement.Rotation=App.Rotation(App.Vector(0,0,1),N)
    o.setExpression('Placement.Base.y',None);o.setExpression('Placement.Base.z',None)
    o.Placement.Base=App.Vector(x,y,40.3+y/3)-N*2
    return o

def lid():
    blank=profile('InclinedPanelProfile',[(-45,25.3),(45,55.3),(45,58.5),(-45,28.5)])
    tools=[]
    for i,x in enumerate([-28,0,28],1):tools.append(hole('IndicatorHole'+str(i),'Dimensions.IndicatorDiameter',x,16))
    for i,x in enumerate([-24,24],1):tools.append(hole('SwitchHole'+str(i),'Dimensions.SwitchDiameter',x,-18))
    for i,(x,y) in enumerate([(-60,-35),(60,-35),(60,35),(-60,35)],1):
        tools.append(cb.cylinder('ScrewHole'+str(i),'3.4 mm','10 mm',str(x)+' mm',str(y)+' mm',str(38+y/3)+' mm'))
    cb.lid=cb.cut('Lid',blank,cb.fusion('PanelHoleTools',tools));cb.lid.Label='LID / sloped removable control panel'
    cb.show_only([cb.base,cb.lid]);Gui.activeDocument().activeView().fitAll();cb.frame('04-sloped-panel')

def resize(d):cb.resize_switches(d)
def explode():cb.explode(32)
def assemble():cb.assemble()

def populated():
    cb.hardware=cb.doc.addObject('App::DocumentObjectGroup','IllustrativeHardware')
    cb.hardware.Label='Illustrative controls / excluded from exports'
    for i,(x,y,r,color) in enumerate([(-28,16,4,(.1,.8,.5)),(0,16,4,(1,.6,.1)),(28,16,4,(.9,.15,.15)),(-24,-18,8,(.08,.12,.16)),(24,-18,8,(.1,.6,.7))],1):
        v=App.Vector(x,y,43.5+y/3)
        ring=Part.makeCylinder(r+2,1.5,v,N).cut(Part.makeCylinder(r,2,v,N))
        cb.preview_part('Bezel'+str(i),ring,(.55,.6,.65))
        cb.preview_part('Control'+str(i),Part.makeCylinder(r,3.5,v,N),color)
    import Draft
    for t,x,y,size in [('DESK / 02',0,32,3.7),('READY',-28,6,2.2),('RUN',0,6,2.2),('ALERT',28,6,2.2),('POWER',-24,-34,2.5),('MODE',24,-34,2.5)]:
        font_file=os.environ.get('FAH_FREECAD_FONT')
        if not font_file:raise RuntimeError('Set FAH_FREECAD_FONT to a local TrueType font for visual labels')
        lab=Draft.make_shapestring(String=t,FontFile=font_file,Size=size,Tracking=0);cb.doc.recompute()
        rot=App.Rotation(App.Vector(1,0,0),math.degrees(math.atan(1/3)))
        local=App.Vector(-lab.Shape.BoundBox.XLength/2,0,0)
        lab.Placement=App.Placement(App.Vector(x,y,43.5+y/3)+rot.multVec(local)+N*.04,rot)
        lab.ViewObject.ShapeColor=(.08,.12,.17);cb.hardware.addObject(lab)
    cb.doc.recompute();Gui.activeDocument().activeView().fitAll();cb.frame('06-assembled')

def turntable():cb.turntable(5)
def export():return cb.verify_export()
