import os
import control_box_template as cb
from control_box_template import App,Gui,Part

def init(out):
    cb.init(out,'Vented_Wall_Control')
    cb.doc.Label='Vented Wall Control / concept'
    cb.NAVY=(0.12,0.38,0.43)

def outside(): cb.outside()
def hollow(): cb.hollow()
def supports(): cb.supports()

def mounts():
    ears=[]
    for i,x in enumerate([-75,75],1):
        e=cb.box('MountEarBlank'+str(i),'24 mm','24 mm','4 mm','0 mm')
        e.setExpression('Placement.Base.x',None);e.Placement.Base.x=x-12
        cb.doc.recompute()
        ears.append(cb.round_vertical('RoundedMountEar'+str(i),e,5))
    joined=cb.fusion('ShellWithWallMounts',[cb.base]+ears)
    holes=[cb.cylinder('WallScrewTool'+str(i),'5.5 mm','6 mm',str(x)+' mm','0 mm','-1 mm') for i,x in enumerate([-79,79],1)]
    cb.base=cb.cut('WallMountedBase',joined,cb.fusion('WallMountHoleTools',holes))
    cb.base.Label='BASE / wall mounting ears + cable entry'
    cb.show_only([cb.base]);Gui.activeDocument().activeView().fitAll();cb.frame('04-wall-mounts')

def lid(): cb.lid_holes()

def vents():
    tools=[]
    for side,x in enumerate([-50,50]):
        for j,y in enumerate([-23,-13,-3,7,17,27]):
            t=cb.box('VentSlot%d_%d'%(side,j),'3 mm','7 mm','6 mm','49 mm')
            t.setExpression('Placement.Base.x',None);t.setExpression('Placement.Base.y',None)
            t.Placement.Base.x=x-1.5;t.Placement.Base.y=y-3.5;tools.append(t)
    cb.doc.recompute()
    cb.lid=cb.cut('VentedLid',cb.lid,cb.fusion('VentSlotTools',tools))
    cb.lid.Label='LID / 12 vents + light and switch holes'
    cb.show_only([cb.base,cb.lid]);cb.style(cb.lid,cb.SILVER);cb.frame('05-vented-lid')

def resize(d):cb.resize_switches(d)
def explode():cb.explode(35)
def assemble():cb.assemble()
def populated():cb.populated()
def turntable():cb.turntable(5)
def export():return cb.verify_export()
