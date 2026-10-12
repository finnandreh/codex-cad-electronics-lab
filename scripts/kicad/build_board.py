from pathlib import Path
import os,json,math,heapq,itertools,xml.etree.ElementTree as ET
import pcbnew as p
ROOT=Path(os.environ.get('CAD_LAB_WORKSPACE',Path.cwd())).resolve();OUT=Path(os.environ.get('CODEX_PULSE_OUT',ROOT/'build/Codex-Pulse-5V')).resolve();d=json.loads((OUT/'DESIGN.json').read_text());NAME=d['name']
expected={}
for c in d['components']:
    if c['ref'].startswith('#'):continue
    for pin,net in c['pins'].items():expected[(c['ref'],pin)]=net
xml=ET.parse(str(OUT/'NETLIST.xml'));actual={}
for net in xml.findall('.//nets/net'):
    for node in net.findall('node'):
        if not node.attrib['ref'].startswith('#'):actual[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name'].removeprefix('/')
assert expected==actual,dict(expected=expected,actual=actual)
manager=p.GetSettingsManager();assert manager.LoadProject(str(OUT/(NAME+'.kicad_pro')))
b=p.BOARD();b.SetProject(manager.Prj());lib=Path(os.environ.get('KICAD_FOOTPRINTS','/usr/share/kicad/footprints'))
mm=lambda x:p.FromMM(float(x));V=lambda x,y:p.VECTOR2I(mm(x),mm(y))
netnames=sorted(set(expected.values()));nets={}
for name in netnames:n=p.NETINFO_ITEM(b,'/'+name);b.Add(n);nets[name]=n
footprints=[];pads=[]
for c in d['components']:
    if not c['footprint']:continue
    family,item=c['footprint'].split(':');fp=p.FootprintLoad(str(lib/(family+'.pretty')),item);assert fp
    fp.SetReference(c['ref']);fp.SetValue(c['value']);fp.SetFPID(p.LIB_ID(family,item));fp.SetPosition(V(*c['pcb']))
    fp.SetPath(p.KIID_PATH('/'+d['schematic_uuid']+'/'+c['uuid']))
    fp.Reference().SetTextSize(V(.9,.9));fp.Reference().SetTextThickness(mm(.13));fp.Value().SetVisible(False)
    b.Add(fp);footprints.append(fp)
    for pad in fp.Pads():
        number=pad.GetNumber();assert number in c['pins'],(c['ref'],number);net=c['pins'][number];pad.SetNet(nets[net]);pos=pad.GetPosition();sz=pad.GetSize()
        pads.append(dict(ref=c['ref'],number=number,net=net,x=p.ToMM(pos.x),y=p.ToMM(pos.y),sx=p.ToMM(sz.x),sy=p.ToMM(sz.y),pad=pad))
for i,(x,y) in enumerate([(3.5,3.5),(46.5,3.5),(3.5,31.5),(46.5,31.5)],1):
    fp=p.FootprintLoad(str(lib/'MountingHole.pretty'),'MountingHole_3.2mm_M3');fp.SetFPID(p.LIB_ID('MountingHole','MountingHole_3.2mm_M3'));fp.SetReference('H'+str(i));fp.SetPosition(V(x,y));fp.Value().SetVisible(False);fp.Reference().SetVisible(False);b.Add(fp)
    pads.append(dict(ref='H'+str(i),number='',net='',x=x,y=y,sx=3.2,sy=3.2))
for (x1,y1),(x2,y2) in [((0,0),(50,0)),((50,0),(50,35)),((50,35),(0,35)),((0,35),(0,0))]:
    s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(V(x1,y1));s.SetEnd(V(x2,y2));s.SetWidth(mm(.05));s.SetLayer(p.Edge_Cuts);b.Add(s)
def text(value,x,y,size=1):
    t=p.PCB_TEXT(b);t.SetText(value);t.SetPosition(V(x,y));t.SetTextSize(V(size,size));t.SetTextThickness(mm(.15));t.SetLayer(p.F_SilkS);b.Add(t)
text('CODEX PULSE',18,1.7,1.1);text('5V',13,9.5,.85);text('+',5.5,10.16,.85);text('GND',7.62,15.4,.8);text('RESET',20.9,23.2,.8);text('0.69 Hz',39,23,.8)
grid=.254;NX=int(50/grid)+1;NY=int(35/grid)+1
snap=lambda x:int(round(x/grid));point=lambda a:(snap(a['x']),snap(a['y']))
base_blocked={}
def blocked_for(net):
    if net in base_blocked:return base_blocked[net]
    blocked=set()
    for a in pads:
        if a['net']==net:continue
        rx=a['sx']/2+.42;ry=a['sy']/2+.42
        for ix in range(max(0,snap(a['x']-rx)-1),min(NX,snap(a['x']+rx)+2)):
            for iy in range(max(0,snap(a['y']-ry)-1),min(NY,snap(a['y']+ry)+2)):
                if abs(ix*grid-a['x'])<=rx and abs(iy*grid-a['y'])<=ry:blocked.add((ix,iy))
    base_blocked[net]=blocked;return blocked
copper=[{},{}];via_block=set()
for a in pads:
    rx=a['sx']/2+.65;ry=a['sy']/2+.65
    for ix in range(max(0,snap(a['x']-rx)-1),min(NX,snap(a['x']+rx)+2)):
        for iy in range(max(0,snap(a['y']-ry)-1),min(NY,snap(a['y']+ry)+2)):
            if abs(ix*grid-a['x'])<=rx and abs(iy*grid-a['y'])<=ry:via_block.add((ix,iy))
directions=[(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
def route(start,goal,net):
    blocked=blocked_for(net);q=[];dist={};prev={};counter=itertools.count()
    def h(x,y):return math.hypot(x-goal[0],y-goal[1])
    for layer in (0,1):s=(*start,layer);dist[s]=0;prev[s]=None;heapq.heappush(q,(h(*start),next(counter),s))
    def available(x,y,l):return 1.0<=x*grid<=49.0 and 1.0<=y*grid<=34.0 and (x,y) not in blocked and copper[l].get((x,y),net)==net
    target=None
    while q:
        _,_,s=heapq.heappop(q);x,y,l=s
        if (x,y)==goal:target=s;break
        choices=[]
        for dx,dy in directions:
            xx,yy=x+dx,y+dy
            if not available(xx,yy,l):continue
            if dx and dy and (not available(x+dx,y,l) or not available(x,y+dy,l)):continue
            choices.append(((xx,yy,l),math.hypot(dx,dy)))
        if (x,y) not in via_block and available(x,y,1-l):choices.append(((x,y,1-l),25))
        for nxt,cost in choices:
            previous=prev[s]
            if previous and previous[2]==s[2]==nxt[2] and (s[0]-previous[0],s[1]-previous[1])!=(nxt[0]-s[0],nxt[1]-s[1]):cost+=.12
            nd=dist[s]+cost
            if nd+1e-8<dist.get(nxt,1e99):dist[nxt]=nd;prev[nxt]=s;heapq.heappush(q,(nd+h(nxt[0],nxt[1]),next(counter),nxt))
    assert target is not None,('Unroutable',net,start,goal)
    path=[]
    while target is not None:path.append(target);target=prev[target]
    return path[::-1]
def occupy(x,y,l,net,radius=.57):
    rr=math.ceil(radius/grid)
    for dx in range(-rr,rr+1):
        for dy in range(-rr,rr+1):
            if math.hypot(dx,dy)*grid<=radius:copper[l][(x+dx,y+dy)]=net
routes=[]
for net in sorted(netnames,key=lambda n:len([a for a in pads if a['net']==n])):
    terminals=[a for a in pads if a['net']==net];connected=[terminals.pop(0)]
    while terminals:
        _,a,z=min((math.hypot(a['x']-z['x'],a['y']-z['y']),i,j) for i,a in enumerate(connected) for j,z in enumerate(terminals));a=connected[a];z=terminals.pop(z);path=route(point(a),point(z),net)
        # Compress straight grid runs; through-hole pads connect the layers at endpoints.
        simplified=[path[0]]
        for k in range(1,len(path)-1):
            before=path[k-1];cur=path[k];after=path[k+1]
            if (cur[0]-before[0],cur[1]-before[1],cur[2]-before[2])!=(after[0]-cur[0],after[1]-cur[1],after[2]-cur[2]):simplified.append(cur)
        simplified.append(path[-1]);points=[(a['x'],a['y'],path[0][2])]+[(x*grid,y*grid,l) for x,y,l in simplified]+[(z['x'],z['y'],path[-1][2])]
        for s,t in zip(points,points[1:]):
            if s[2]!=t[2]:
                v=p.PCB_VIA(b);v.SetPosition(V(s[0],s[1]));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[net]);b.Add(v)
            elif math.hypot(s[0]-t[0],s[1]-t[1])>1e-6:
                tr=p.PCB_TRACK(b);tr.SetStart(V(s[0],s[1]));tr.SetEnd(V(t[0],t[1]));tr.SetWidth(mm(.3));tr.SetLayer(p.F_Cu if s[2]==0 else p.B_Cu);tr.SetNet(nets[net]);b.Add(tr)
        for x,y,l in path:occupy(x,y,l,net)
        for s,t in zip(path,path[1:]):
            if s[2]!=t[2]:
                for l in (0,1):occupy(s[0],s[1],l,net,.72)
        routes.append(dict(net=net,from_pad=a['ref']+'.'+a['number'],to_pad=z['ref']+'.'+z['number'],grid_nodes=len(path)));connected.append(z)
        print('Routed',routes[-1],flush=True)
b.BuildConnectivity()
dest=OUT/(NAME+'.kicad_pcb');assert not dest.exists();p.SaveBoard(str(dest),b);print('All eight nets explicitly routed; native PCB saved',flush=True)
check=p.LoadBoard(str(dest));check.SetProject(manager.Prj());check.BuildConnectivity();p.WriteDRCReport(check,str(OUT/'DRC-v1.txt'),p.EDA_UNITS_MILLIMETRES,True)
(OUT/'ROUTING-v1.json').write_text(json.dumps(dict(routes=routes,track_count=len(list(check.GetTracks())),footprints=len(list(check.GetFootprints())),nets=netnames,schematic_netlist_matches=True,ground='Explicit routed GND on two layers; no zone fill dependence',drc='See DRC-v1.txt; do not claim passed until report inspected'),indent=2))
print('Native PCB saved, reloaded; all nets routed and DRC report generated',dest)
