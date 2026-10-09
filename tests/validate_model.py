from pathlib import Path
import json
import sys
import numpy as np
import trimesh
from pygltflib import GLTF2

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from generate_model import DEFAULTS
cfg=DEFAULTS|json.loads((root/'dimensions.json').read_text())
p=root/'dist/lavadero-piedra.glb'
gltf=GLTF2().load(str(p))
scene=trimesh.load(p,force='scene')
mesh=next(iter(scene.geometry.values())).copy()
mesh.merge_vertices(merge_tex=True,merge_norm=True)

def hits_down(x,z):
    origin=np.array([x,.5,z]);direction=np.array([0.,-1.,0.])
    tri=mesh.triangles
    e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
    h=np.cross(np.broadcast_to(direction,e2.shape),e2)
    a=np.einsum('ij,ij->i',e1,h)
    valid=np.abs(a)>1e-12
    f=np.divide(1,a,out=np.zeros_like(a),where=valid)
    s=origin-tri[:,0]
    u=f*np.einsum('ij,ij->i',s,h)
    q=np.cross(s,e1)
    v=f*np.einsum('j,ij->i',direction,q)
    t=f*np.einsum('ij,ij->i',e2,q)
    mask=valid&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-8)
    return np.unique(np.round(.5-t[mask],7)).tolist()[::-1]

floor_hits=hits_down(.10,0)
rim_hits=hits_down(0,-.24)
drain_hits=hits_down(cfg['drain_x'],cfg['drain_z'])
checks={
    'opens_with_pygltflib':gltf.asset.version=='2.0',
    'opens_with_trimesh':len(scene.geometry)==1,
    'watertight_stone_volume':bool(mesh.is_watertight),
    'consistent_face_winding':bool(mesh.is_winding_consistent),
    'single_connected_component':len(mesh.split(only_watertight=False))==1,
    'positive_volume':bool(mesh.volume>0),
    'no_degenerate_triangles':bool(np.min(mesh.area_faces)>1e-14),
    'finite_vertices':bool(np.isfinite(mesh.vertices).all()),
    'dimensions_match':bool(np.allclose(mesh.extents,[cfg['width'],cfg['height'],cfg['depth']],atol=1e-6)),
    'open_drain_through_base':len(drain_hits)==0,
    'basin_floor_depth':len(floor_hits)==2 and -.037<floor_hits[0]<-.029,
    'stone_below_floor':len(floor_hits)==2 and abs(floor_hits[-1]+.09)<1e-5,
    'no_rear_faucet_hole':len(rim_hits)==2 and abs(rim_hits[0]-.09)<1e-5,
    'embedded_images':len(gltf.images)==2 and all(i.bufferView is not None and i.uri is None for i in gltf.images),
    'no_external_buffers':all(b.uri is None for b in gltf.buffers),
    'non_metallic_material':gltf.materials[0].pbrMetallicRoughness.metallicFactor==0,
    'under_10000_triangles':len(mesh.faces)<10000,
    'under_2MB':p.stat().st_size<2_000_000,
}
report={'checks':checks,'passed':all(checks.values()),'triangles':len(mesh.faces),'welded_vertices':len(mesh.vertices),'euler_number':mesh.euler_number,'volume_m3':float(mesh.volume),'minimum_triangle_area_m2':float(mesh.area_faces.min()),'rays':{'basin_y':floor_hits,'rear_rim_y':rim_hits,'drain_y':drain_hits},'basis':'Independent GLB import, edge topology, winding, bounds and vertical ray intersections. Visual likeness and assumed dimensions require owner review.'}
(root/'dist/geometry-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report['passed'],[k for k,v in checks.items() if not v]
