from pathlib import Path
import argparse
import io
import json
import math
import struct
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = {
    'width': 0.90, 'depth': 0.55, 'height': 0.18,
    'basin_width': 0.56, 'basin_depth': 0.31,
    'floor_width': 0.45, 'floor_depth': 0.20,
    'basin_center_x': 0.035, 'basin_center_z': -0.012,
    'basin_drop': 0.12, 'floor_fall': 0.006,
    'drain_diameter': 0.045, 'drain_x': -0.11, 'drain_z': 0.0,
    'edge_bevel': 0.0015, 'texture_tile_m': 0.30,
    'texture_size': 1024, 'seed': 9021, 'radial_segments': 128
}


def make_textures(cfg):
    rng = np.random.default_rng(cfg['seed'])
    size = cfg['texture_size']
    grain = rng.normal(0, 1.1, (size, size, 1))
    arr = np.clip(np.array([233, 231, 225])[None, None, :] + grain, 0, 255).astype('uint8')
    img = Image.fromarray(arr, 'RGB')
    draw = ImageDraw.Draw(img)
    for count, rmin, rmax, low, high in [(2600, .25, .8, 180, 222), (900, .65, 1.6, 138, 201), (85, 1.2, 2.5, 134, 184)]:
        for _ in range(count):
            x, y = rng.uniform(0, size, 2)
            rx = rng.uniform(rmin, rmax)
            ry = rx * rng.uniform(.45, 1.35)
            tone = int(rng.integers(low, high))
            color = (tone + 3, tone + 2, tone)
            for ox in (-size, 0, size):
                for oy in (-size, 0, size):
                    draw.ellipse((x-rx+ox,y-ry+oy,x+rx+ox,y+ry+oy), fill=color)
    base = io.BytesIO()
    img.save(base, format='JPEG', quality=94, subsampling=0)
    luminance = np.asarray(img).mean(axis=2)
    orm = np.zeros((size,size,3), dtype=np.uint8)
    orm[:,:,0] = 255
    orm[:,:,1] = np.clip(145 + (233-luminance)*.22, 0,255).astype(np.uint8)
    rough = io.BytesIO()
    Image.fromarray(orm).save(rough, format='PNG', optimize=True)
    return base.getvalue(), rough.getvalue()


def rounded_rect_ray(theta, cx, cz, w, d, radius, ox, oz):
    direction = np.array([math.cos(theta), math.sin(theta)])
    lo, hi = 0.0, 2 * max(w,d)
    half = np.array([w/2,d/2])
    for _ in range(48):
        mid = (lo+hi)/2
        p = np.array([ox-cx,oz-cz]) + direction*mid
        q = np.abs(p) - half + radius
        sdf = np.linalg.norm(np.maximum(q,0)) + min(max(q),0) - radius
        if sdf <= 0:
            lo = mid
        else:
            hi = mid
    return np.array([ox,oz]) + direction*((lo+hi)/2)


def build_mesh(c):
    w,d,h,b = (c[k] for k in ('width','depth','height','edge_bevel'))
    cx,cz = c['basin_center_x'],c['basin_center_z']
    ox,oz = c['drain_x'],c['drain_z']
    bw,bd,fw,fd = (c[k] for k in ('basin_width','basin_depth','floor_width','floor_depth'))
    top,bottom = h/2,-h/2
    floor = top-c['basin_drop']
    r = c['drain_diameter']/2
    assert floor-c['floor_fall'] > bottom + .015
    assert abs(cx)+bw/2 < w/2-b and abs(cz)+bd/2 < d/2-b
    assert abs(ox-cx)+r+.01 < fw/2 and abs(oz-cz)+r+.01 < fd/2
    specs = [
        (0,0,w-2*b,d-2*b,.001, bottom),
        (0,0,w,d,.0018,bottom+b),
        (0,0,w,d,.0018,top-b),
        (0,0,w-2*b,d-2*b,.001,top),
        (cx,cz,bw+2*b,bd+2*b,.0045,top),
        (cx,cz,bw,bd,.003,top-b),
        (cx,cz,fw+.006,fd+.006,.008,floor+.004),
        (cx,cz,fw,fd,.006,floor),
    ]
    angles = list(np.linspace(0,2*math.pi,c['radial_segments'],endpoint=False))
    for sx,sz,sw,sd,sr,sy in specs:
        for xx in (-1,1):
            for zz in (-1,1):
                for px,pz in [(sx+xx*(sw/2-sr),sz+zz*sd/2),(sx+xx*sw/2,sz+zz*(sd/2-sr))]:
                    angles.append(math.atan2(pz-oz,px-ox)%(2*math.pi))
    angles = sorted(set(round(a,9) for a in angles))
    rings = []
    for sx,sz,sw,sd,sr,sy in specs:
        points=[rounded_rect_ray(a,sx,sz,sw,sd,sr,ox,oz) for a in angles]
        rings.append(np.array([[p[0],sy,p[1]] for p in points]))
    circle=lambda radius,y: np.array([[ox+radius*math.cos(a),y,oz+radius*math.sin(a)] for a in angles])
    lip = circle(r+.0015,floor-c['floor_fall'])
    rings += [rings[-1]*.5+lip*.5, lip, circle(r,floor-c['floor_fall']-.0015), circle(r,bottom+.001), circle(r+.001,bottom)]
    vertices = np.concatenate(rings)
    n = len(angles)
    faces=[]
    regions=[]
    labels=['bottom_bevel','exterior','top_bevel','rim','basin_lip','basin_walls','floor_fillet','basin_floor','basin_floor','drain_lip','drain_tube','bottom_drain_bevel','underside']
    for j in range(len(rings)):
        k=(j+1)%len(rings)
        for i in range(n):
            ni=(i+1)%n
            a,b1,c1,d1=j*n+i,j*n+ni,k*n+ni,k*n+i
            faces += [[a,b1,c1],[a,c1,d1]]
            regions += [labels[j],labels[j]]
    faces=np.array(faces,dtype=np.uint32)
    tri=vertices[faces]
    vol=np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6
    if vol<0:
        faces=faces[:,[0,2,1]]
    tri=vertices[faces]
    cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    normals=np.zeros_like(vertices)
    for j,ring in enumerate(rings):
        for i,p in enumerate(ring):
            if j in (0,12):
                normal=np.array([0.,-1.,0.])
            elif j in (3,4):
                normal=np.array([0.,1.,0.])
            elif j in (1,2,5,6):
                sx,sz,sw,sd,sr,_=specs[j]
                delta=p[[0,2]]-np.array([sx,sz])
                q=np.abs(delta)-np.array([sw/2-sr,sd/2-sr])
                gradient=np.maximum(q,0)*np.sign(delta)
                gradient/=np.linalg.norm(gradient)
                if j in (1,2):
                    normal=np.array([gradient[0],0.,gradient[1]])
                else:
                    slope=np.array([(bw-fw-.006)/2,(bd-fd-.006)/2])/(top-b-floor-.004)
                    normal=np.array([-gradient[0],float(np.dot(np.abs(gradient),slope)),-gradient[1]])
            elif j in (10,11):
                normal=np.array([ox-p[0],0.,oz-p[2]])
            else:
                radial=p[[0,2]]-np.array([ox,oz])
                radius=np.linalg.norm(radial)
                span=np.linalg.norm(rings[7][i][[0,2]]-np.array([ox,oz]))-(r+.0015)
                gradient=radial/max(radius,1e-9)*c['floor_fall']/span
                normal=np.array([-gradient[0],1.,-gradient[1]])
            normals[j*n+i]=normal/np.linalg.norm(normal)
    # UV seams duplicate render vertices only; geometry remains a single welded solid.
    verts=[]; norms=[]; uv=[]; indices=[]; lookup={}
    for face,normal in zip(faces,cross):
        axis=int(np.argmax(np.abs(normal)))
        for idx in face:
            key=(int(idx),axis)
            if key not in lookup:
                lookup[key]=len(verts)
                p=vertices[idx]
                coords=([p[2],p[1]] if axis==0 else [p[0],p[2]] if axis==1 else [p[0],p[1]])
                verts.append(p); norms.append(normals[idx]); uv.append(np.array(coords)/c['texture_tile_m'])
            indices.append(lookup[key])
    return (np.array(verts,dtype='<f4'),np.array(norms,dtype='<f4'),np.array(uv,dtype='<f4'),np.array(indices,dtype='<u2'),vertices,faces,regions)


def export_glb(out,cfg,mesh,textures):
    pos,norm,uv,idx,*_=mesh
    chunks=[]; views=[]; accessors=[]; offset=0
    def add_data(data,target=None):
        nonlocal offset
        while offset%4:
            chunks.append(b'\0');offset+=1
        v={'buffer':0,'byteOffset':offset,'byteLength':len(data)}
        if target: v['target']=target
        views.append(v);chunks.append(data);offset+=len(data)
        return len(views)-1
    def acc(array,kind,component,target,minmax=False):
        bv=add_data(array.tobytes(),target)
        a={'bufferView':bv,'componentType':component,'count':len(array),'type':kind}
        if minmax:a.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
        accessors.append(a);return len(accessors)-1
    pi=acc(pos,'VEC3',5126,34962,True);ni=acc(norm,'VEC3',5126,34962);ui=acc(uv,'VEC2',5126,34962);ii=acc(idx,'SCALAR',5123,34963)
    base=add_data(textures[0]);rough=add_data(textures[1])
    gltf={'asset':{'version':'2.0','generator':'Aqua Piedra | parametric sink v1'},'scene':0,
          'scenes':[{'name':'Lavadero de piedra','nodes':[0]}],
          'nodes':[{'name':'Lavadero_Piedra_90x55','mesh':0}],
          'meshes':[{'name':'Cuerpo_piedra_con_poza_y_desague','primitives':[{'attributes':{'POSITION':pi,'NORMAL':ni,'TEXCOORD_0':ui},'indices':ii,'material':0,'mode':4}]}],
          'materials':[{'name':'Piedra_crema_moteada_satinada','doubleSided':False,'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':1,'metallicRoughnessTexture':{'index':1}}}],
          'textures':[{'sampler':0,'source':0},{'sampler':0,'source':1}],
          'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497}],
          'images':[{'name':'stone_basecolor','bufferView':base,'mimeType':'image/jpeg'},{'name':'stone_roughness','bufferView':rough,'mimeType':'image/png'}],
          'buffers':[{'byteLength':offset}],'bufferViews':views,'accessors':accessors,
          'extras':{'units':'meters','axis':'Y-up; front = +Z','dimensions_assumed':cfg,'reference':'Single generated reference image; no rear tap hole; unseen underside estimated'}}
    js=json.dumps(gltf,separators=(',',':')).encode(); js+=b' '*((-len(js))%4)
    blob=b''.join(chunks);blob+=b'\0'*((-len(blob))%4)
    out.write_bytes(struct.pack('<III',0x46546c67,2,12+8+len(js)+8+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',type=Path,default=ROOT/'dimensions.json')
    parser.add_argument('--out',type=Path,default=ROOT/'dist')
    args=parser.parse_args()
    cfg=DEFAULTS.copy()
    if args.config.exists():cfg.update(json.loads(args.config.read_text()))
    args.out.mkdir(parents=True,exist_ok=True)
    mesh=build_mesh(cfg);textures=make_textures(cfg)
    path=args.out/'lavadero-piedra.glb'
    export_glb(path,cfg,mesh,textures)
    (args.out/'stone-basecolor.jpg').write_bytes(textures[0])
    (args.out/'stone-roughness.png').write_bytes(textures[1])
    stats={'triangles':len(mesh[3])//3,'render_vertices':len(mesh[0]),'geometric_vertices':len(mesh[4]),'meshes':1,'materials':1,'embedded_textures':2,'file_bytes':path.stat().st_size,'dimensions_m':[cfg['width'],cfg['height'],cfg['depth']],'basin_depth_m':cfg['basin_drop'],'drain_floor_depth_m':cfg['basin_drop']+cfg['floor_fall'],'drain_diameter_m':cfg['drain_diameter']}
    (args.out/'model-stats.json').write_text(json.dumps(stats,indent=2))
    print(json.dumps(stats,indent=2))

if __name__=='__main__':main()
