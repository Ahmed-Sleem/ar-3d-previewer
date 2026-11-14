import zipfile, os, shutil, glob, re, io
from PIL import Image
from pxr import Usd, UsdGeom, UsdUtils, Sdf, UsdShade
for f in sorted(glob.glob('final/*.usdz')):
    n=os.path.basename(f)[:-5]; d=f'work/{n}'; shutil.rmtree(d,ignore_errors=True); zipfile.ZipFile(f).extractall(d)
    root=open(f'{d}/model.usda').read()
    for p in glob.glob(f'{d}/textures/*.png'):
        im=Image.open(p); b=os.path.basename(p)
        if im.mode=='RGBA' and im.getchannel('A').getextrema()[0] < 255: continue   # keep real alpha
        im.convert('RGB').save(p[:-4]+'.jpg', quality=88, optimize=True); os.remove(p); root=root.replace(b, b[:-4]+'.jpg')
    for g in glob.glob(f'{d}/geometries/*.usda'):
        st=Usd.Stage.Open(g)
        for prim in st.Traverse():
            if prim.IsA(UsdGeom.Mesh): UsdGeom.Mesh(prim).CreateDoubleSidedAttr(True)
        st.GetRootLayer().Export(g[:-5]+'.usdc'); os.remove(g); b=os.path.basename(g); root=root.replace(b, b[:-5]+'.usdc')
    open(f'{d}/model.usda','w').write(root)
    out=os.path.abspath(f'final/{n}.usdz'); os.remove(f); cwd=os.getcwd(); os.chdir(d)
    ok=UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath('model.usda'), out); os.chdir(cwd)
    s=Usd.Stage.Open(out); bb=UsdGeom.BBoxCache(Usd.TimeCode.Default(),['default','render']).ComputeWorldBound(s.GetPseudoRoot()).ComputeAlignedRange()
    meshes=[p for p in s.Traverse() if p.IsA(UsdGeom.Mesh)]
    z=zipfile.ZipFile(out)
    print(n, ok, round(os.path.getsize(out)/1e6,2),'MB size',[round(x,2) for x in bb.GetSize()],'minY',round(bb.GetMin()[1],3),'meshes',len(meshes),'dbl',all(UsdGeom.Mesh(m).GetDoubleSidedAttr().Get() for m in meshes),'bound',all(UsdShade.MaterialBindingAPI(m).ComputeBoundMaterial()[0] for m in meshes),'first',z.infolist()[0].filename,'align',all((i.header_offset+30+len(i.filename.encode())+len(i.extra))%64==0 for i in z.infolist()),'stored',all(i.compress_type==0 for i in z.infolist()),[i.filename.split('.')[-1] for i in z.infolist()])
